from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.tender import Alert, Tender, TenderMatch, User
from app.services.users import get_user_alert_preferences, has_verified_whatsapp

DISPATCHABLE_STATUSES = ("pending", "retrying", "blocked")


def generate_alerts(db: Session, users: list[User], *, default_min_score: float = 60) -> dict:
    tenders = db.execute(select(Tender).order_by(Tender.id.asc())).scalars().all()
    created = 0
    for user in users:
        user_profile_min_score = (
            float((user.company_profile.alert_preferences_json or {}).get("min_score", default_min_score))
            if getattr(user, "company_profile", None) is not None
            else default_min_score
        )
        preferences = get_user_alert_preferences(user, default_min_score=user_profile_min_score)
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
            Alert.delivery_channel.in_(("whatsapp", "email")),
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
    if not preferences.get("receive_deadlines", True) or tender.deadline_date is None:
        return 0

    now = datetime.now(tz=UTC)
    if tender.deadline_date <= now:
        return 0

    created = 0
    deadlines = [
        ("deadline_7d", tender.deadline_date - timedelta(days=7)),
        ("deadline_3d", tender.deadline_date - timedelta(days=3)),
        ("deadline_24h", tender.deadline_date - timedelta(hours=24)),
    ]

    for alert_type, scheduled_for in deadlines:
        if scheduled_for <= now:
            continue
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
                    "deadline_date": tender.deadline_date.isoformat(),
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
