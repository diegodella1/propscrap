from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.tender import Alert, Tender, TenderMatch, TenderState, User
from app.services.users import get_user_alert_preferences, has_verified_telegram, has_verified_whatsapp

DISPATCHABLE_STATUSES = ("pending", "retrying", "blocked")
SAVED_STATES = {"saved", "evaluating", "presenting"}


def generate_alerts(db: Session, users: list[User], *, default_min_score: float = 60) -> dict:
    tenders = db.execute(
        select(Tender)
        .options(selectinload(Tender.enrichments))
        .order_by(Tender.id.asc())
    ).scalars().all()
    created = 0
    for user in users:
        company_preferences = _get_company_alert_preferences(user, default_min_score=default_min_score)
        preferences = _get_effective_alert_preferences(user, company_preferences=company_preferences)
        for tender in tenders:
            created += _ensure_relevance_alerts(db, tender, user, preferences=preferences)
            created += _ensure_deadline_alerts(db, tender, user, preferences=preferences)
    db.commit()
    return {"created_alerts": created}


def list_recent_alerts(db: Session, limit: int = 100) -> list[Alert]:
    return db.execute(
        select(Alert).order_by(Alert.scheduled_for.asc(), Alert.id.desc()).limit(limit)
    ).scalars().all()


def list_dispatchable_alerts(db: Session, *, limit: int) -> list[Alert]:
    now = datetime.now(tz=UTC)
    return db.execute(
        select(Alert)
        .options(joinedload(Alert.user))
        .where(
            Alert.delivery_channel.in_(("whatsapp", "email", "telegram")),
            Alert.delivery_status.in_(DISPATCHABLE_STATUSES),
            Alert.scheduled_for <= now,
        )
        .order_by(Alert.scheduled_for.asc(), Alert.id.asc())
        .limit(limit)
    ).scalars().all()


def _ensure_relevance_alerts(db: Session, tender: Tender, user: User, *, preferences: dict) -> int:
    if not preferences.get("receive_relevant", True):
        return 0
    if not user.company_profile_id:
        return 0

    match = db.execute(
        select(TenderMatch)
        .where(
            TenderMatch.tender_id == tender.id,
            TenderMatch.company_profile_id == user.company_profile_id,
        )
        .limit(1)
    ).scalar_one_or_none()
    if match is None or float(match.score) < float(preferences["min_score"]):
        return 0

    created = 0
    for channel in _eligible_channels(user, preferences):
        created += _create_alert_if_missing(
            db,
            tender=tender,
            user=user,
            alert_type="new_relevant",
            scheduled_for=datetime.now(tz=UTC),
            channel=channel,
            payload_snapshot={
                "title": tender.title,
                "score": str(match.score),
                "score_band": match.score_band,
            },
        )
    return created


def _ensure_deadline_alerts(db: Session, tender: Tender, user: User, *, preferences: dict) -> int:
    if not preferences.get("receive_deadlines", True):
        return 0
    if preferences.get("deadline_only_for_saved", True) and not _is_saved_for_user(db, tender, user):
        return 0

    now = datetime.now(tz=UTC)
    created = 0
    for event_key, event_date in _iter_detected_deadlines(tender):
        if event_date <= now:
            continue
        for offset_hours in preferences.get("deadline_offsets_hours", [168, 72, 24]):
            scheduled_for = event_date - timedelta(hours=int(offset_hours))
            if scheduled_for <= now:
                continue
            suffix = _format_deadline_offset_label(int(offset_hours))
            alert_type = f"{event_key}_{suffix}"
            for channel in _eligible_channels(user, preferences):
                created += _create_alert_if_missing(
                    db,
                    tender=tender,
                    user=user,
                    alert_type=alert_type,
                    scheduled_for=scheduled_for,
                    channel=channel,
                    payload_snapshot={
                        "title": tender.title,
                        "event_key": event_key,
                        "event_date": event_date.isoformat(),
                        "offset_hours": str(offset_hours),
                    },
                )
    return created


def _eligible_channels(user: User, preferences: dict) -> list[str]:
    channels: list[str] = []
    requested_channels = set(preferences.get("channels", []))
    if "dashboard" in requested_channels or not requested_channels:
        channels.append("dashboard")
    if "whatsapp" in requested_channels and has_verified_whatsapp(user):
        channels.append("whatsapp")
    if "email" in requested_channels and user.email:
        channels.append("email")
    if "telegram" in requested_channels and has_verified_telegram(user):
        channels.append("telegram")
    return channels


def _create_alert_if_missing(
    db: Session,
    *,
    tender: Tender,
    user: User,
    alert_type: str,
    scheduled_for: datetime,
    channel: str,
    payload_snapshot: dict,
) -> int:
    if _find_existing_alert(db, tender.id, user.id, alert_type, channel):
        return 0

    alert = Alert(
        tender_id=tender.id,
        user_id=user.id,
        alert_type=alert_type,
        scheduled_for=scheduled_for,
        delivery_channel=channel,
        delivery_status="pending",
        payload_snapshot=payload_snapshot,
    )
    db.add(alert)
    return 1


def _find_existing_alert(
    db: Session,
    tender_id: int,
    user_id: int,
    alert_type: str,
    channel: str,
) -> Alert | None:
    return db.execute(
        select(Alert).where(
            Alert.tender_id == tender_id,
            Alert.user_id == user_id,
            Alert.alert_type == alert_type,
            Alert.delivery_channel == channel,
        )
    ).scalar_one_or_none()


def _get_company_alert_preferences(user: User, *, default_min_score: float) -> dict:
    raw = (
        user.company_profile.alert_preferences_json
        if getattr(user, "company_profile", None) is not None and isinstance(user.company_profile.alert_preferences_json, dict)
        else {}
    )
    offsets = raw.get("deadline_offsets_hours", [168, 72, 24])
    if not isinstance(offsets, list):
        offsets = [168, 72, 24]
    return {
        "min_score": float(raw.get("min_score", default_min_score)),
        "receive_relevant": bool(raw.get("receive_relevant", True)),
        "receive_deadlines": bool(raw.get("receive_deadlines", True)),
        "deadline_only_for_saved": bool(raw.get("deadline_only_for_saved", True)),
        "deadline_offsets_hours": [int(value) for value in offsets if isinstance(value, (int, float, str)) and str(value).isdigit()],
    }


def _get_effective_alert_preferences(user: User, *, company_preferences: dict) -> dict:
    user_preferences = get_user_alert_preferences(user, default_min_score=company_preferences["min_score"])
    return {
        "channels": user_preferences.get("channels", ["dashboard"]),
        "min_score": max(float(company_preferences["min_score"]), float(user_preferences.get("min_score", 60))),
        "receive_relevant": bool(company_preferences.get("receive_relevant", True))
        and bool(user_preferences.get("receive_relevant", True)),
        "receive_deadlines": bool(company_preferences.get("receive_deadlines", True))
        and bool(user_preferences.get("receive_deadlines", True)),
        "deadline_only_for_saved": bool(company_preferences.get("deadline_only_for_saved", True)),
        "deadline_offsets_hours": company_preferences.get("deadline_offsets_hours", [168, 72, 24]) or [168, 72, 24],
    }


def _is_saved_for_user(db: Session, tender: Tender, user: User) -> bool:
    state = db.execute(
        select(TenderState)
        .where(TenderState.tender_id == tender.id, TenderState.user_id == user.id)
        .order_by(TenderState.id.desc())
        .limit(1)
    ).scalar_one_or_none()
    return bool(state and state.state in SAVED_STATES)


def _iter_detected_deadlines(tender: Tender) -> list[tuple[str, datetime]]:
    items: list[tuple[str, datetime]] = []
    if tender.deadline_date is not None:
        items.append(("submission_deadline", tender.deadline_date))
    if tender.opening_date is not None:
        items.append(("opening_date", tender.opening_date))

    latest_enrichment = tender.enrichments[0] if tender.enrichments else None
    extracted = latest_enrichment.extracted_deadlines if latest_enrichment and isinstance(latest_enrichment.extracted_deadlines, dict) else {}
    for key, raw_value in extracted.items():
        parsed = _parse_event_datetime(raw_value)
        if parsed is None:
            continue
        if key == "deadline_date" and tender.deadline_date is not None:
            continue
        if key == "opening_date" and tender.opening_date is not None:
            continue
        items.append((str(key).strip().lower().replace(" ", "_"), parsed))
    return items


def _parse_event_datetime(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed


def _format_deadline_offset_label(hours: int) -> str:
    if hours % 24 == 0:
        days = hours // 24
        return f"{days}d"
    return f"{hours}h"
