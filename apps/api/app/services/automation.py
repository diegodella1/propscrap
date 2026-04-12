from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import ValidationError
from app.jobs.dispatch_alerts import run_alert_dispatch
from app.jobs.enrich_tender import enrich_pending_tenders
from app.jobs.generate_alerts import run_alert_generation
from app.jobs.ingest_source import ingest_source
from app.jobs.match_tenders import match_all_tenders
from app.models.tender import AutomationSetting, Source
from app.services.runtime_settings import get_automation_settings
from app.services.source_registry import CONNECTORS


def should_run_automation(settings: AutomationSetting, now: datetime | None = None) -> bool:
    if not settings.is_enabled:
        return False

    current_time = now or datetime.now(tz=UTC)
    if settings.last_run_started_at is None:
        return True

    next_run_at = settings.last_run_started_at + timedelta(hours=settings.ingestion_interval_hours)
    return current_time >= next_run_at


def run_automation_cycle(db: Session) -> dict:
    settings = get_automation_settings(db)
    if (
        settings.last_run_started_at is not None
        and (
            settings.last_run_finished_at is None
            or settings.last_run_finished_at < settings.last_run_started_at
        )
    ):
        raise ValidationError("Automation cycle already running")

    started_at = datetime.now(tz=UTC)
    settings.last_run_started_at = started_at
    settings.last_run_finished_at = None
    settings.last_error_message = None
    db.add(settings)
    db.commit()

    active_sources = db.execute(select(Source).where(Source.is_active.is_(True)).order_by(Source.id.asc())).scalars().all()
    ingested_sources: list[dict] = []
    skipped_sources: list[dict] = []

    try:
        for source in active_sources:
            connector_key = source.connector_slug or source.slug
            if connector_key not in CONNECTORS:
                skipped_sources.append(
                    {
                        "source_id": source.id,
                        "slug": source.slug,
                        "connector_slug": source.connector_slug,
                        "reason": "connector_not_implemented",
                    }
                )
                continue
            ingested_sources.append(ingest_source(db, source.slug))

        enrichment_result = enrich_pending_tenders(db)
        match_result = match_all_tenders(db)
        alert_result = run_alert_generation(db)
        dispatch_result = run_alert_dispatch(db)

        finished_at = datetime.now(tz=UTC)
        summary = {
            "sources_total": len(active_sources),
            "sources_ingested": len(ingested_sources),
            "sources_skipped": skipped_sources,
            "ingestion_results": ingested_sources,
            "enrichment": enrichment_result,
            "match": match_result,
            "alerts": alert_result,
            "dispatch": dispatch_result,
        }
        settings.last_run_finished_at = finished_at
        settings.last_success_at = finished_at
        settings.last_cycle_summary = summary
        settings.last_error_message = None
        db.add(settings)
        db.commit()
        return summary
    except Exception as exc:
        settings = get_automation_settings(db)
        settings.last_run_finished_at = datetime.now(tz=UTC)
        settings.last_error_message = str(exc)
        db.add(settings)
        db.commit()
        raise


def run_automation_tick(db: Session, now: datetime | None = None) -> dict:
    settings = get_automation_settings(db)
    db.commit()
    if not should_run_automation(settings, now=now):
        return {
            "status": "skipped",
            "reason": "interval_not_reached" if settings.is_enabled else "disabled",
            "ingestion_interval_hours": settings.ingestion_interval_hours,
            "last_run_started_at": settings.last_run_started_at.isoformat() if settings.last_run_started_at else None,
        }
    summary = run_automation_cycle(db)
    return {"status": "executed", "summary": summary}
