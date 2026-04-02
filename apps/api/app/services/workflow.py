from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import ValidationError
from app.models.tender import TenderState

ALLOWED_STATES = {"new", "seen", "saved", "discarded", "evaluating", "presenting"}


def upsert_tender_state(
    db: Session,
    *,
    tender_id: int,
    user_id: int,
    state: str,
    notes: str | None = None,
) -> TenderState:
    if state not in ALLOWED_STATES:
        raise ValidationError(f"Invalid state: {state}")

    existing = db.execute(
        select(TenderState).where(TenderState.tender_id == tender_id, TenderState.user_id == user_id)
    ).scalar_one_or_none()
    if existing is None:
        existing = TenderState(tender_id=tender_id, user_id=user_id, state=state)
        db.add(existing)

    existing.state = state
    existing.notes = notes
    existing.updated_at = datetime.now(tz=UTC)
    return existing
