from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.errors import ConfigurationError, ExternalServiceError, NotFoundError, ValidationError
from app.models.tender import Tender, TenderEnrichment
from app.services.documents import get_tender_with_documents
from app.jobs.process_tender import process_tender
from app.services.runtime_settings import get_automation_settings
from app.services.llm_enrichment import enrich_tender_text


def enrich_tender(db: Session, tender_id: int) -> dict:
    tender = get_tender_with_documents(db, tender_id)
    if tender is None:
        raise NotFoundError(f"Tender not found: {tender_id}")

    process_tender(db, tender.id)
    tender = get_tender_with_documents(db, tender.id)
    if tender is None:
        raise NotFoundError(f"Tender not found: {tender_id}")

    enrichment = _get_or_create_enrichment(db, tender.id)
    enrichment.enrichment_status = "running"
    db.add(enrichment)
    db.commit()

    body_text = _pick_body_text(tender)
    if not body_text:
        enrichment.enrichment_status = "skipped"
        db.add(enrichment)
        db.commit()
        raise ValidationError("Tender has no usable text for enrichment")

    try:
        automation_settings = get_automation_settings(db)
        result = enrich_tender_text(
            title=tender.title,
            source_name=tender.source.name,
            body_text=body_text,
            openai_api_key=automation_settings.openai_api_key_override,
            openai_model=automation_settings.openai_model_override,
            master_prompt=automation_settings.llm_master_prompt,
        )
    except (ConfigurationError, ExternalServiceError):
        enrichment.enrichment_status = "failed"
        db.add(enrichment)
        db.commit()
        raise
    except Exception:
        enrichment.enrichment_status = "failed"
        db.add(enrichment)
        db.commit()
        raise

    enrichment.llm_model = result.model
    enrichment.summary_short = result.payload.get("summary_short")
    enrichment.summary_structured_json = result.payload
    enrichment.key_requirements = result.payload.get("key_requirements")
    enrichment.risk_flags = result.payload.get("risk_flags")
    enrichment.extracted_deadlines = result.payload.get("key_dates")
    enrichment.enrichment_status = "success"
    db.add(enrichment)
    db.commit()

    return {"tender_id": tender.id, "status": "success", "model": result.model}


def enrich_pending_tenders(db: Session, limit: int | None = None) -> dict:
    settings = get_settings()
    if not settings.llm_enabled or not settings.openai_api_key:
        return {"status": "skipped", "reason": "llm_not_configured", "processed": 0}

    batch_limit = limit or settings.llm_enrichment_batch_size
    candidate_ids = db.execute(
        select(Tender.id)
        .outerjoin(TenderEnrichment, TenderEnrichment.tender_id == Tender.id)
        .where(
            or_(
                TenderEnrichment.id.is_(None),
                TenderEnrichment.enrichment_status.in_(["pending", "failed", "skipped"]),
            )
        )
        .order_by(Tender.id.desc())
        .limit(batch_limit)
    ).scalars().all()

    processed = 0
    succeeded = 0
    skipped = 0
    failed = 0
    errors: list[dict] = []

    for tender_id in candidate_ids:
        processed += 1
        try:
            result = enrich_tender(db, tender_id)
            if result["status"] == "success":
                succeeded += 1
        except ValidationError as exc:
            skipped += 1
            errors.append({"tender_id": tender_id, "status": "skipped", "detail": exc.detail})
        except (ConfigurationError, ExternalServiceError) as exc:
            failed += 1
            errors.append({"tender_id": tender_id, "status": "failed", "detail": exc.detail})
        except Exception as exc:
            failed += 1
            errors.append({"tender_id": tender_id, "status": "failed", "detail": str(exc)})

    return {
        "status": "ok",
        "processed": processed,
        "succeeded": succeeded,
        "skipped": skipped,
        "failed": failed,
        "batch_limit": batch_limit,
        "errors": errors[:10],
    }


def _get_or_create_enrichment(db: Session, tender_id: int) -> TenderEnrichment:
    enrichment = db.execute(
        select(TenderEnrichment).where(TenderEnrichment.tender_id == tender_id)
    ).scalar_one_or_none()
    if enrichment is not None:
        return enrichment

    enrichment = TenderEnrichment(tender_id=tender_id)
    db.add(enrichment)
    db.flush()
    return enrichment


def _pick_body_text(tender) -> str | None:
    for document in tender.documents:
        for text in document.texts:
            if text.extracted_text and text.text_length > 100:
                return text.extracted_text
    return tender.description_raw
