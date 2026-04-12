from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import NotFoundError
from app.models.tender import Source
from app.services.dedupe.service import apply_tender_updates, find_existing_tender
from app.services.normalization.tenders import normalize_tender
from app.services.source_registry import CONNECTORS
from app.services.sources import ensure_source, finish_source_run, start_source_run


def ingest_source(db: Session, source_slug: str) -> dict:
    source = db.execute(select(Source).where(Source.slug == source_slug)).scalar_one_or_none()
    connector_key = source.connector_slug if source and source.connector_slug else source_slug
    connector_cls = CONNECTORS.get(connector_key)
    if not connector_cls:
        raise NotFoundError(f"Unknown source slug: {source_slug}")

    connector = connector_cls()
    if source is None:
        source = ensure_source(
            db,
            slug=source_slug,
            name=connector.name,
            source_type="portal",
            scraping_mode="coded",
            connector_slug=connector.slug,
            base_url=connector.base_url,
        )
        db.flush()
    else:
        source.name = source.name or connector.name
        source.source_type = source.source_type or "portal"
        source.scraping_mode = source.scraping_mode or "coded"
        source.connector_slug = connector.slug
        if not source.base_url:
            source.base_url = connector.base_url
        db.add(source)
        db.flush()

    run = start_source_run(db, source.id)
    db.commit()
    db.refresh(source)
    db.refresh(run)

    items_found = 0
    items_new = 0

    try:
        records = connector.fetch()
        items_found = len(records)

        for record in records:
            candidate = normalize_tender(source.id, record)
            existing = find_existing_tender(db, source.id, candidate.external_id, candidate.dedupe_hash)
            if existing:
                apply_tender_updates(existing, candidate)
                continue

            db.add(candidate)
            items_new += 1

        source.last_run_at = datetime.now(tz=UTC)
        finish_source_run(db, run, status="success", items_found=items_found, items_new=items_new)
        db.commit()
        return {
            "source": source.slug,
            "status": "success",
            "items_found": items_found,
            "items_new": items_new,
        }
    except Exception as exc:
        finish_source_run(
            db,
            run,
            status="failed",
            items_found=items_found,
            items_new=items_new,
            error_message=str(exc),
        )
        db.commit()
        raise
