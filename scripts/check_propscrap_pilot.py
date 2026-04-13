from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
import sys

from sqlalchemy import func, select

API_DIR = Path(__file__).resolve().parents[1] / "apps" / "api"
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from app.db.session import SessionLocal
from app.models.tender import AutomationSetting, Source, SourceRun, Tender
from app.services.runtime_settings import get_automation_settings


def main() -> int:
    now = datetime.now(tz=UTC)
    max_source_run_age = now - timedelta(hours=30)
    max_cycle_age = now - timedelta(hours=30)
    max_tender_age = now - timedelta(days=7)

    db = SessionLocal()
    try:
        settings = get_automation_settings(db)
        db.flush()

        active_sources = db.execute(select(Source).where(Source.is_active.is_(True)).order_by(Source.id.asc())).scalars().all()
        latest_runs = {
            source.id: db.execute(
                select(SourceRun)
                .where(SourceRun.source_id == source.id)
                .order_by(SourceRun.started_at.desc(), SourceRun.id.desc())
                .limit(1)
            ).scalar_one_or_none()
            for source in active_sources
        }

        total_tenders = db.execute(select(func.count()).select_from(Tender)).scalar_one()
        latest_tender_created_at = db.execute(select(Tender.created_at).order_by(Tender.created_at.desc()).limit(1)).scalar_one_or_none()

        failures: list[str] = []
        warnings: list[str] = []

        if not settings.is_enabled:
            failures.append("automation disabled")

        if settings.last_run_started_at is None:
            failures.append("automation has never started")
        elif settings.last_run_started_at < max_cycle_age:
            failures.append(f"last automation cycle too old: {settings.last_run_started_at.isoformat()}")

        if settings.last_error_message:
            warnings.append(f"last automation error: {settings.last_error_message}")

        for source in active_sources:
            run = latest_runs[source.id]
            if run is None:
                failures.append(f"source {source.slug} has no runs")
                continue
            if run.started_at < max_source_run_age:
                failures.append(f"source {source.slug} last run too old: {run.started_at.isoformat()}")
            if run.status not in {"success", "completed"}:
                warnings.append(f"source {source.slug} last run status={run.status}")
            if run.error_message:
                warnings.append(f"source {source.slug} last error={run.error_message}")

        if total_tenders == 0:
            failures.append("database has zero tenders")
        elif latest_tender_created_at is not None and latest_tender_created_at < max_tender_age:
            warnings.append(f"latest tender is old: {latest_tender_created_at.isoformat()}")

        print(
            {
                "status": "ok" if not failures else "failed",
                "active_sources": len(active_sources),
                "tenders_total": total_tenders,
                "last_run_started_at": settings.last_run_started_at.isoformat() if settings.last_run_started_at else None,
                "last_success_at": settings.last_success_at.isoformat() if settings.last_success_at else None,
                "failures": failures,
                "warnings": warnings,
            }
        )
        return 0 if not failures else 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
