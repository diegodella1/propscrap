from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tender import Source, SourceRun


def ensure_source(
    db: Session, *, slug: str, name: str, source_type: str, base_url: str, is_active: bool = True
) -> Source:
    existing = db.execute(select(Source).where(Source.slug == slug)).scalar_one_or_none()
    if existing:
        existing.name = name
        existing.source_type = source_type
        existing.base_url = base_url
        existing.is_active = is_active
        return existing

    source = Source(
        slug=slug,
        name=name,
        source_type=source_type,
        base_url=base_url,
        is_active=is_active,
    )
    db.add(source)
    return source


def start_source_run(db: Session, source_id: int) -> SourceRun:
    run = SourceRun(source_id=source_id, status="running")
    db.add(run)
    db.flush()
    return run


def finish_source_run(
    db: Session,
    run: SourceRun,
    *,
    status: str,
    items_found: int,
    items_new: int,
    error_message: str | None = None,
) -> SourceRun:
    run.status = status
    run.finished_at = datetime.now(tz=UTC)
    run.items_found = items_found
    run.items_new = items_new
    run.error_message = error_message
    return run

