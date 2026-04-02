from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserRead(BaseModel):
    id: int
    company_profile_id: int | None = None
    email: str
    full_name: str
    company_name: str | None = None
    role: str
    is_active: bool
    whatsapp_number: str | None = None
    whatsapp_opt_in: bool = False
    whatsapp_verified_at: datetime | None = None
    alert_preferences_json: dict | None = None

    model_config = ConfigDict(from_attributes=True)


class AdminAlertRead(BaseModel):
    id: int
    tender_id: int
    user_id: int
    alert_type: str
    scheduled_for: datetime
    sent_at: datetime | None = None
    delivery_channel: str
    delivery_status: str
    delivery_attempts: int
    last_error_message: str | None = None
    provider_message_id: str | None = None
    payload_snapshot: dict | None = None

    model_config = ConfigDict(from_attributes=True)


class SourceAdminRead(BaseModel):
    id: int
    name: str
    slug: str
    source_type: str
    base_url: str
    is_active: bool
    last_run_at: datetime | None = None
    connector_available: bool

    model_config = ConfigDict(from_attributes=True)


class SourceCreateRequest(BaseModel):
    name: str
    slug: str
    source_type: str
    base_url: str
    is_active: bool = True


class SourceUpdateRequest(BaseModel):
    name: str | None = None
    slug: str | None = None
    source_type: str | None = None
    base_url: str | None = None
    is_active: bool | None = None


class UserUpdateRequest(BaseModel):
    full_name: str | None = None
    company_name: str | None = None
    role: str | None = None
    is_active: bool | None = None
    whatsapp_number: str | None = None
    whatsapp_opt_in: bool | None = None
    whatsapp_verified: bool | None = None
    alert_preferences_json: dict | None = None


class CompanyProfileAdminRead(BaseModel):
    id: int
    company_name: str
    company_description: str
    sectors: list[str] | None = None
    include_keywords: list[str] | None = None
    exclude_keywords: list[str] | None = None
    jurisdictions: list[str] | None = None
    preferred_buyers: list[str] | None = None
    min_amount: str | None = None
    max_amount: str | None = None
    alert_preferences_json: dict | None = None

    model_config = ConfigDict(from_attributes=True)


class CompanyProfileUpdateRequest(BaseModel):
    company_name: str
    company_description: str
    sectors: list[str] | None = None
    include_keywords: list[str] | None = None
    exclude_keywords: list[str] | None = None
    jurisdictions: list[str] | None = None
    preferred_buyers: list[str] | None = None
    min_amount: str | None = None
    max_amount: str | None = None
    alert_preferences_json: dict | None = None


class AutomationSettingsRead(BaseModel):
    id: int
    is_enabled: bool
    ingestion_interval_hours: int
    openai_api_key_configured: bool = False
    openai_model: str | None = None
    llm_master_prompt: str | None = None
    last_run_started_at: datetime | None = None
    last_run_finished_at: datetime | None = None
    last_success_at: datetime | None = None
    last_error_message: str | None = None
    last_cycle_summary: dict | None = None

    model_config = ConfigDict(from_attributes=True)


class AutomationSettingsUpdateRequest(BaseModel):
    is_enabled: bool | None = None
    ingestion_interval_hours: int | None = None
    openai_api_key: str | None = None
    openai_model: str | None = None
    llm_master_prompt: str | None = None
