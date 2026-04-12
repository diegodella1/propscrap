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
    db.add(settings)
    db.flush()
    return settings
