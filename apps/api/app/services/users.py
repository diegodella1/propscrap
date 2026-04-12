from __future__ import annotations

from datetime import UTC, datetime
import re

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.services.auth import hash_password
from app.services.company_profiles import apply_company_lookup_result, ensure_user_company_profile
from app.services.company_registry import lookup_company_by_cuit, validate_cuit
from app.errors import ValidationError
from app.models.tender import User

DEFAULT_ALERT_PREFERENCES = {
    "min_score": 60,
    "channels": ["dashboard"],
    "receive_relevant": True,
    "receive_deadlines": True,
}
ALLOWED_ALERT_CHANNELS = {"dashboard", "whatsapp", "email", "telegram"}
PHONE_PATTERN = re.compile(r"^\+[1-9]\d{7,14}$")
TELEGRAM_CHAT_PATTERN = re.compile(r"^-?\d{4,}$")


def ensure_demo_user(db: Session) -> User:
    existing = db.execute(select(User).where(User.email == "demo@licitacionesia.local")).scalar_one_or_none()
    if existing:
        _ensure_user_defaults(existing)
        ensure_user_company_profile(db, existing)
        return existing

    user = User(
        email="demo@licitacionesia.local",
        full_name="Demo User",
        company_name="Tecnologia Sanitaria Integrada SA",
        password_hash=hash_password("Demo1234"),
        role="analyst",
        is_active=True,
        alert_preferences_json=DEFAULT_ALERT_PREFERENCES.copy(),
    )
    db.add(user)
    db.flush()
    ensure_user_company_profile(db, user)
    return user


def ensure_platform_admin_user(db: Session) -> User:
    existing = db.execute(select(User).where(User.email == "admin@propscrap.local")).scalar_one_or_none()
    if existing:
        _ensure_user_defaults(existing)
        return existing

    user = User(
        email="admin@propscrap.local",
        full_name="Platform Admin",
        company_name="Propscrap Platform",
        password_hash=hash_password("Admin1234"),
        role="admin",
        is_active=True,
        alert_preferences_json=DEFAULT_ALERT_PREFERENCES.copy(),
    )
    db.add(user)
    db.flush()
    ensure_user_company_profile(db, user)
    return user


def ensure_demo_company_admin_user(db: Session) -> User:
    existing = db.execute(select(User).where(User.email == "manager@licitacionesia.local")).scalar_one_or_none()
    if existing:
        _ensure_user_defaults(existing)
        ensure_user_company_profile(db, existing)
        return existing

    user = User(
        email="manager@licitacionesia.local",
        full_name="Company Admin",
        company_name="Tecnologia Sanitaria Integrada SA",
        password_hash=hash_password("Manager1234"),
        role="manager",
        is_active=True,
        alert_preferences_json=DEFAULT_ALERT_PREFERENCES.copy(),
    )
    db.add(user)
    db.flush()
    ensure_user_company_profile(db, user)
    return user


def list_active_users(db: Session) -> list[User]:
    users = db.execute(
        select(User)
        .options(selectinload(User.company_profile))
        .where(User.is_active.is_(True))
        .order_by(User.id.asc())
    ).scalars().all()
    for user in users:
        _ensure_user_defaults(user)
    return users


def update_user(
    db: Session,
    user: User,
    *,
    full_name: str | None = None,
    company_name: str | None = None,
    cuit: str | None = None,
    role: str | None = None,
    is_active: bool | None = None,
    whatsapp_number: str | None = None,
    whatsapp_opt_in: bool | None = None,
    whatsapp_verified: bool | None = None,
    telegram_chat_id: str | None = None,
    telegram_opt_in: bool | None = None,
    telegram_verified: bool | None = None,
    alert_preferences_json: dict | None = None,
) -> User:
    _ensure_user_defaults(user)

    if full_name is not None:
        user.full_name = full_name.strip()
    if company_name is not None:
        user.company_name = company_name.strip() if company_name.strip() else None
    if cuit is not None:
        normalized_cuit = validate_cuit(cuit) if cuit.strip() else None
        if normalized_cuit:
            company_result = lookup_company_by_cuit(normalized_cuit)
            apply_company_lookup_result(db, user=user, company_result=company_result)
        else:
            user.cuit = None
    if role is not None:
        user.role = role.strip()
    if is_active is not None:
        user.is_active = is_active

    if whatsapp_number is not None:
        user.whatsapp_number = _normalize_whatsapp_number(whatsapp_number)
        if user.whatsapp_number is None:
            user.whatsapp_verified_at = None

    if whatsapp_opt_in is not None:
        user.whatsapp_opt_in = whatsapp_opt_in

    if telegram_chat_id is not None:
        user.telegram_chat_id = _normalize_telegram_chat_id(telegram_chat_id)
        if user.telegram_chat_id is None:
            user.telegram_verified_at = None

    if telegram_opt_in is not None:
        user.telegram_opt_in = telegram_opt_in

    if alert_preferences_json is not None:
        user.alert_preferences_json = normalize_alert_preferences(alert_preferences_json)

    if whatsapp_verified is not None:
        if whatsapp_verified:
            if not user.whatsapp_number:
                raise ValidationError("Cannot verify WhatsApp without a valid phone number")
            user.whatsapp_verified_at = user.whatsapp_verified_at or datetime.now(tz=UTC)
        else:
            user.whatsapp_verified_at = None

    if telegram_verified is not None:
        if telegram_verified:
            if not user.telegram_chat_id:
                raise ValidationError("Cannot verify Telegram without a valid chat id")
            user.telegram_verified_at = user.telegram_verified_at or datetime.now(tz=UTC)
        else:
            user.telegram_verified_at = None

    _validate_telegram_configuration(user)
    _validate_whatsapp_configuration(user)
    db.add(user)
    db.flush()
    return user


def normalize_alert_preferences(payload: dict | None) -> dict:
    if payload is None:
        return DEFAULT_ALERT_PREFERENCES.copy()
    if not isinstance(payload, dict):
        raise ValidationError("Alert preferences must be an object")

    channels = payload.get("channels", DEFAULT_ALERT_PREFERENCES["channels"])
    if not isinstance(channels, list):
        raise ValidationError("Alert channels must be a list")

    normalized_channels = []
    for channel in channels:
        value = str(channel).strip().lower()
        if value not in ALLOWED_ALERT_CHANNELS:
            raise ValidationError(f"Unsupported alert channel: {channel}")
        if value not in normalized_channels:
            normalized_channels.append(value)

    min_score = payload.get("min_score", DEFAULT_ALERT_PREFERENCES["min_score"])
    try:
        normalized_min_score = int(min_score)
    except (TypeError, ValueError) as exc:
        raise ValidationError("Alert min_score must be numeric") from exc

    if normalized_min_score < 0 or normalized_min_score > 100:
        raise ValidationError("Alert min_score must be between 0 and 100")

    return {
        "min_score": normalized_min_score,
        "channels": normalized_channels or DEFAULT_ALERT_PREFERENCES["channels"].copy(),
        "receive_relevant": bool(payload.get("receive_relevant", True)),
        "receive_deadlines": bool(payload.get("receive_deadlines", True)),
    }


def get_user_alert_preferences(user: User, *, default_min_score: float = 60) -> dict:
    raw_preferences = user.alert_preferences_json if isinstance(user.alert_preferences_json, dict) else {}
    _ensure_user_defaults(user)
    preferences = normalize_alert_preferences(user.alert_preferences_json)
    if "min_score" not in raw_preferences or raw_preferences.get("min_score") is None:
        preferences["min_score"] = int(default_min_score)
    return preferences


def has_verified_whatsapp(user: User) -> bool:
    return bool(user.whatsapp_number and user.whatsapp_opt_in and user.whatsapp_verified_at)


def has_verified_telegram(user: User) -> bool:
    return bool(user.telegram_chat_id and user.telegram_opt_in and user.telegram_verified_at)


def _ensure_user_defaults(user: User) -> None:
    user.alert_preferences_json = normalize_alert_preferences(user.alert_preferences_json)


def _validate_whatsapp_configuration(user: User) -> None:
    if user.whatsapp_opt_in and not user.whatsapp_number:
        raise ValidationError("WhatsApp opt-in requires a valid WhatsApp number")

    channels = set((user.alert_preferences_json or {}).get("channels", []))
    if "whatsapp" in channels and not user.whatsapp_opt_in:
        raise ValidationError("WhatsApp channel requires opt-in to be enabled")

    if "whatsapp" in channels and user.whatsapp_number and not user.whatsapp_verified_at:
        raise ValidationError("WhatsApp channel requires the number to be verified")


def _validate_telegram_configuration(user: User) -> None:
    if user.telegram_opt_in and not user.telegram_chat_id:
        raise ValidationError("Telegram opt-in requires a valid Telegram chat id")

    channels = set((user.alert_preferences_json or {}).get("channels", []))
    if "telegram" in channels and not user.telegram_opt_in:
        raise ValidationError("Telegram channel requires opt-in to be enabled")

    if "telegram" in channels and user.telegram_chat_id and not user.telegram_verified_at:
        raise ValidationError("Telegram channel requires the chat id to be verified")


def _normalize_whatsapp_number(raw_value: str) -> str | None:
    value = raw_value.strip()
    if not value:
        return None

    compact = re.sub(r"[^\d+]", "", value)
    if compact.startswith("00"):
        compact = f"+{compact[2:]}"
    if not compact.startswith("+"):
        compact = f"+{compact}"

    if not PHONE_PATTERN.fullmatch(compact):
        raise ValidationError("WhatsApp number must use E.164 format, for example +5491123456789")
    return compact


def _normalize_telegram_chat_id(raw_value: str) -> str | None:
    value = raw_value.strip()
    if not value:
        return None
    if not TELEGRAM_CHAT_PATTERN.fullmatch(value):
        raise ValidationError("Telegram chat id must be numeric, for example 123456789 or -1001234567890")
    return value
