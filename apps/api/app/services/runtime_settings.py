from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import ValidationError
from app.models.tender import AutomationSetting


DEFAULT_AUTOMATION_SETTINGS_ID = 1


def get_automation_settings(db: Session) -> AutomationSetting:
    settings = db.execute(
        select(AutomationSetting).where(AutomationSetting.id == DEFAULT_AUTOMATION_SETTINGS_ID)
    ).scalar_one_or_none()
    if settings is not None:
        return settings

    settings = AutomationSetting(
        id=DEFAULT_AUTOMATION_SETTINGS_ID,
        is_enabled=True,
        ingestion_interval_hours=1,
    )
    db.add(settings)
    db.flush()
    return settings


def update_automation_settings(
    db: Session,
    settings: AutomationSetting,
    *,
    is_enabled: bool | None = None,
    ingestion_interval_hours: int | None = None,
    openai_api_key: str | None = None,
    openai_model: str | None = None,
    llm_master_prompt: str | None = None,
    contact_email: str | None = None,
    contact_whatsapp_number: str | None = None,
    contact_telegram_handle: str | None = None,
    demo_booking_url: str | None = None,
    resend_api_key: str | None = None,
    resend_from_email: str | None = None,
    email_delivery_enabled: bool | None = None,
    whatsapp_enabled: bool | None = None,
    whatsapp_provider: str | None = None,
    whatsapp_meta_token: str | None = None,
    whatsapp_meta_phone_number_id: str | None = None,
    whatsapp_api_version: str | None = None,
    telegram_enabled: bool | None = None,
    telegram_bot_token: str | None = None,
) -> AutomationSetting:
    if is_enabled is not None:
        settings.is_enabled = is_enabled
    if ingestion_interval_hours is not None:
        if ingestion_interval_hours < 1 or ingestion_interval_hours > 168:
            raise ValidationError("ingestion_interval_hours must be between 1 and 168")
        settings.ingestion_interval_hours = ingestion_interval_hours
    if openai_api_key is not None:
        normalized_key = openai_api_key.strip()
        settings.openai_api_key_override = normalized_key or None
    if openai_model is not None:
        normalized_model = openai_model.strip()
        settings.openai_model_override = normalized_model or None
    if llm_master_prompt is not None:
        normalized_prompt = llm_master_prompt.strip()
        settings.llm_master_prompt = normalized_prompt or None
    if contact_email is not None:
        normalized_contact_email = contact_email.strip().lower()
        settings.contact_email = normalized_contact_email or None
    if contact_whatsapp_number is not None:
        normalized_whatsapp = contact_whatsapp_number.strip()
        settings.contact_whatsapp_number = normalized_whatsapp or None
    if contact_telegram_handle is not None:
        normalized_telegram = contact_telegram_handle.strip()
        settings.contact_telegram_handle = normalized_telegram or None
    if demo_booking_url is not None:
        normalized_demo_url = demo_booking_url.strip()
        settings.demo_booking_url = normalized_demo_url or None
    if resend_api_key is not None:
        normalized_resend_key = resend_api_key.strip()
        settings.resend_api_key_override = normalized_resend_key or None
    if resend_from_email is not None:
        normalized_from_email = resend_from_email.strip().lower()
        settings.resend_from_email = normalized_from_email or None
    if email_delivery_enabled is not None:
        settings.email_delivery_enabled = email_delivery_enabled
    if whatsapp_enabled is not None:
        settings.whatsapp_enabled_override = whatsapp_enabled
    if whatsapp_provider is not None:
        normalized_provider = whatsapp_provider.strip().lower()
        if normalized_provider not in {"mock", "meta"}:
            raise ValidationError("whatsapp_provider must be one of: mock, meta")
        settings.whatsapp_provider_override = normalized_provider
    if whatsapp_meta_token is not None:
        normalized_whatsapp_token = whatsapp_meta_token.strip()
        settings.whatsapp_meta_token_override = normalized_whatsapp_token or None
    if whatsapp_meta_phone_number_id is not None:
        normalized_phone_id = whatsapp_meta_phone_number_id.strip()
        settings.whatsapp_meta_phone_number_id_override = normalized_phone_id or None
    if whatsapp_api_version is not None:
        normalized_api_version = whatsapp_api_version.strip()
        settings.whatsapp_meta_api_version_override = normalized_api_version or None
    if telegram_enabled is not None:
        settings.telegram_enabled_override = telegram_enabled
    if telegram_bot_token is not None:
        normalized_telegram_token = telegram_bot_token.strip()
        settings.telegram_bot_token_override = normalized_telegram_token or None
    db.add(settings)
    db.flush()
    return settings
