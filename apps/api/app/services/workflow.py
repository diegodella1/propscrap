from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import NotFoundError, ValidationError
from app.models.tender import Tender, TenderState

ALLOWED_STATES = {"new", "seen", "saved", "discarded", "evaluating", "presenting"}
DEFAULT_TENDER_ALERT_OVERRIDES = {
    "inherit_company_defaults": True,
    "receive_deadlines": True,
    "deadline_offsets_hours": [],
}


def normalize_tender_alert_overrides(payload: dict | None) -> dict:
    if payload is None:
        return DEFAULT_TENDER_ALERT_OVERRIDES.copy()
    if not isinstance(payload, dict):
        return DEFAULT_TENDER_ALERT_OVERRIDES.copy()

    raw_offsets = payload.get("deadline_offsets_hours", [])
    offsets: list[int] = []
    if isinstance(raw_offsets, list):
        for value in raw_offsets:
            try:
                hours = int(value)
            except (TypeError, ValueError):
                continue
            if hours <= 0:
                continue
            if hours not in offsets:
                offsets.append(hours)
    offsets.sort(reverse=True)

    return {
        "inherit_company_defaults": bool(payload.get("inherit_company_defaults", True)),
        "receive_deadlines": bool(payload.get("receive_deadlines", True)),
        "deadline_offsets_hours": offsets,
    }


def upsert_tender_state(
    db: Session,
    *,
    tender_id: int,
    user_id: int,
    state: str,
    notes: str | None = None,
    alert_overrides_json: dict | None = None,
) -> TenderState:
    if state not in ALLOWED_STATES:
        raise ValidationError(f"Invalid state: {state}")

    tender = db.execute(select(Tender.id).where(Tender.id == tender_id)).scalar_one_or_none()
    if tender is None:
        raise NotFoundError(f"Tender not found: {tender_id}")

    existing = db.execute(
        select(TenderState).where(TenderState.tender_id == tender_id, TenderState.user_id == user_id)
    ).scalar_one_or_none()
    if existing is None:
        existing = TenderState(tender_id=tender_id, user_id=user_id, state=state)
        db.add(existing)

    existing.state = state
    existing.notes = notes
    if alert_overrides_json is not None:
        existing.alert_overrides_json = normalize_tender_alert_overrides(alert_overrides_json)
    elif existing.alert_overrides_json is None:
        existing.alert_overrides_json = DEFAULT_TENDER_ALERT_OVERRIDES.copy()
    existing.updated_at = datetime.now(tz=UTC)
    return existing
