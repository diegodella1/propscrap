from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

from app.services.http_safety import assert_public_https_url
from app.services.source_registry import ALLOWED_CONNECTOR_SLUGS

SourceTypeLiteral = Literal["portal", "boletin", "marketplace", "manual"]
ScrapingModeLiteral = Literal["coded", "api", "html", "pdf", "hybrid"]


class UserRead(BaseModel):
    id: int
    company_profile_id: int | None = None
    cuit: str | None = None
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


class AdminAuditEventRead(BaseModel):
    id: int
    actor_user_id: int | None = None
    action: str
    detail_json: dict | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WhatsappOutboxMessageRead(BaseModel):
    id: str
    provider: str
    to: str
    body: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class SourceAdminRead(BaseModel):
    id: int
    name: str
    slug: str
    source_type: str
    scraping_mode: str
    connector_slug: str | None = None
    base_url: str
    config_json: dict | None = None
    is_active: bool
    last_run_at: datetime | None = None
    connector_available: bool

    model_config = ConfigDict(from_attributes=True)


class SourceCreateRequest(BaseModel):
    name: str
    slug: str
    source_type: SourceTypeLiteral
    scraping_mode: ScrapingModeLiteral = "coded"
    connector_slug: str | None = None
    base_url: str
    config_json: dict | None = None
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip()

    @field_validator("slug")
    @classmethod
    def normalize_slug(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("connector_slug")
    @classmethod
    def validate_connector_slug(cls, v: str | None) -> str | None:
        if v is None or not str(v).strip():
            return None
        s = v.strip().lower()
        if s not in ALLOWED_CONNECTOR_SLUGS:
            allowed = ", ".join(sorted(ALLOWED_CONNECTOR_SLUGS))
            raise ValueError(f"connector_slug must be one of: {allowed}")
        return s

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        s = v.strip()
        assert_public_https_url(s, label="base_url")
        return s


class SourceUpdateRequest(BaseModel):
    name: str | None = None
    slug: str | None = None
    source_type: SourceTypeLiteral | None = None
    scraping_mode: ScrapingModeLiteral | None = None
    connector_slug: str | None = None
    base_url: str | None = None
    config_json: dict | None = None
    is_active: bool | None = None

    @field_validator("name")
    @classmethod
    def strip_name_opt(cls, v: str | None) -> str | None:
        return v.strip() if v is not None else None

    @field_validator("slug")
    @classmethod
    def normalize_slug_opt(cls, v: str | None) -> str | None:
        return v.strip().lower() if v is not None else None

    @field_validator("connector_slug")
    @classmethod
    def validate_connector_slug_opt(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if not str(v).strip():
            return None
        s = v.strip().lower()
        if s not in ALLOWED_CONNECTOR_SLUGS:
            allowed = ", ".join(sorted(ALLOWED_CONNECTOR_SLUGS))
            raise ValueError(f"connector_slug must be one of: {allowed}")
        return s

    @field_validator("base_url")
    @classmethod
    def validate_base_url_opt(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip()
        assert_public_https_url(s, label="base_url")
        return s


class UserUpdateRequest(BaseModel):
    full_name: str | None = None
    company_name: str | None = None
    cuit: str | None = None
    role: str | None = None
    is_active: bool | None = None
    whatsapp_number: str | None = None
    whatsapp_opt_in: bool | None = None
    whatsapp_verified: bool | None = None
    alert_preferences_json: dict | None = None


class CompanyProfileAdminRead(BaseModel):
    id: int
    cuit: str | None = None
    company_name: str
    legal_name: str | None = None
    company_description: str
    sectors: list[str] | None = None
    include_keywords: list[str] | None = None
    exclude_keywords: list[str] | None = None
    jurisdictions: list[str] | None = None
    preferred_buyers: list[str] | None = None
    min_amount: str | None = None
    max_amount: str | None = None
    alert_preferences_json: dict | None = None
    tax_status_json: dict | None = None
    company_data_source: str | None = None
    company_data_updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class CompanyProfileUpdateRequest(BaseModel):
    cuit: str | None = None
    company_name: str
    legal_name: str | None = None
    company_description: str
    sectors: list[str] | None = None
    include_keywords: list[str] | None = None
    exclude_keywords: list[str] | None = None
    jurisdictions: list[str] | None = None
    preferred_buyers: list[str] | None = None
    min_amount: str | None = None
    max_amount: str | None = None
    alert_preferences_json: dict | None = None
    tax_status_json: dict | None = None


class AutomationSettingsRead(BaseModel):
    id: int
    is_enabled: bool
    ingestion_interval_hours: int
    openai_api_key_configured: bool = False
    resend_api_key_configured: bool = False
    email_delivery_enabled: bool = False
    openai_model: str | None = None
    llm_master_prompt: str | None = None
    contact_email: str | None = None
    contact_whatsapp_number: str | None = None
    contact_telegram_handle: str | None = None
    demo_booking_url: str | None = None
    resend_from_email: str | None = None
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
    contact_email: str | None = None
    contact_whatsapp_number: str | None = None
    contact_telegram_handle: str | None = None
    demo_booking_url: str | None = None
    resend_api_key: str | None = None
    resend_from_email: str | None = None
    email_delivery_enabled: bool | None = None


class PublicPlatformSettingsRead(BaseModel):
    contact_email: str | None = None
    contact_whatsapp_number: str | None = None
    contact_telegram_handle: str | None = None
    demo_booking_url: str | None = None
