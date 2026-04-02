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
    db.add(settings)
    db.flush()
    return settings
