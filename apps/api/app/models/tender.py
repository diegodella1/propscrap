from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    source_type: Mapped[str] = mapped_column(String(50))
    scraping_mode: Mapped[str] = mapped_column(String(50), default="coded")
    connector_slug: Mapped[str | None] = mapped_column(String(100), nullable=True)
    base_url: Mapped[str] = mapped_column(Text)
    config_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    runs: Mapped[list["SourceRun"]] = relationship(back_populates="source")
    tenders: Mapped[list["Tender"]] = relationship(back_populates="source")


class SourceRun(Base):
    __tablename__ = "source_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    status: Mapped[str] = mapped_column(String(50))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    items_found: Mapped[int] = mapped_column(default=0)
    items_new: Mapped[int] = mapped_column(default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    source: Mapped["Source"] = relationship(back_populates="runs")


class Tender(Base):
    __tablename__ = "tenders"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str] = mapped_column(String(500))
    description_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    organization: Mapped[str | None] = mapped_column(String(255), nullable=True)
    jurisdiction: Mapped[str | None] = mapped_column(String(255), nullable=True)
    procedure_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    publication_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    deadline_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    opening_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    estimated_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    source_url: Mapped[str] = mapped_column(Text)
    dedupe_hash: Mapped[str] = mapped_column(String(64), index=True)
    status_raw: Mapped[str | None] = mapped_column(String(100), nullable=True)
    detail_html_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    detail_cached_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    source: Mapped["Source"] = relationship(back_populates="tenders")
    documents: Mapped[list["TenderDocument"]] = relationship(back_populates="tender")
    enrichments: Mapped[list["TenderEnrichment"]] = relationship(back_populates="tender")
    matches: Mapped[list["TenderMatch"]] = relationship(back_populates="tender")
    states: Mapped[list["TenderState"]] = relationship(back_populates="tender")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="tender")


class TenderDocument(Base):
    __tablename__ = "tender_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    tender_id: Mapped[int] = mapped_column(ForeignKey("tenders.id"), index=True)
    document_type: Mapped[str] = mapped_column(String(100))
    filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str] = mapped_column(Text)
    download_status: Mapped[str] = mapped_column(String(50), default="pending")
    downloaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tender: Mapped["Tender"] = relationship(back_populates="documents")
    texts: Mapped[list["DocumentText"]] = relationship(back_populates="document")


class DocumentText(Base):
    __tablename__ = "document_texts"

    id: Mapped[int] = mapped_column(primary_key=True)
    tender_document_id: Mapped[int] = mapped_column(ForeignKey("tender_documents.id"), index=True)
    extraction_method: Mapped[str] = mapped_column(String(50))
    extraction_status: Mapped[str] = mapped_column(String(50))
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    text_length: Mapped[int] = mapped_column(default=0)
    confidence_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    document: Mapped["TenderDocument"] = relationship(back_populates="texts")


class TenderEnrichment(Base):
    __tablename__ = "tender_enrichments"

    id: Mapped[int] = mapped_column(primary_key=True)
    tender_id: Mapped[int] = mapped_column(ForeignKey("tenders.id"), index=True)
    llm_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    summary_short: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_structured_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    key_requirements: Mapped[list | None] = mapped_column(JSON, nullable=True)
    risk_flags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    extracted_deadlines: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    enrichment_status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tender: Mapped["Tender"] = relationship(back_populates="enrichments")


class CompanyProfile(Base):
    __tablename__ = "company_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    cuit: Mapped[str | None] = mapped_column(String(11), unique=True, nullable=True, index=True)
    company_name: Mapped[str] = mapped_column(String(255))
    legal_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company_description: Mapped[str] = mapped_column(Text)
    sectors: Mapped[list | None] = mapped_column(JSON, nullable=True)
    include_keywords: Mapped[list | None] = mapped_column(JSON, nullable=True)
    exclude_keywords: Mapped[list | None] = mapped_column(JSON, nullable=True)
    jurisdictions: Mapped[list | None] = mapped_column(JSON, nullable=True)
    preferred_buyers: Mapped[list | None] = mapped_column(JSON, nullable=True)
    min_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    max_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    alert_preferences_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    tax_status_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    company_data_source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    company_data_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    matches: Mapped[list["TenderMatch"]] = relationship(back_populates="company_profile")
    users: Mapped[list["User"]] = relationship(back_populates="company_profile")


class TenderMatch(Base):
    __tablename__ = "tender_matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    tender_id: Mapped[int] = mapped_column(ForeignKey("tenders.id"), index=True)
    company_profile_id: Mapped[int] = mapped_column(ForeignKey("company_profiles.id"), index=True)
    score: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    score_band: Mapped[str] = mapped_column(String(20))
    reasons_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    matched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tender: Mapped["Tender"] = relationship(back_populates="matches")
    company_profile: Mapped["CompanyProfile"] = relationship(back_populates="matches")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_profile_id: Mapped[int | None] = mapped_column(ForeignKey("company_profiles.id"), nullable=True, index=True)
    cuit: Mapped[str | None] = mapped_column(String(11), nullable=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    full_name: Mapped[str] = mapped_column(String(255))
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    whatsapp_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    whatsapp_opt_in: Mapped[bool] = mapped_column(Boolean, default=False)
    whatsapp_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    telegram_chat_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    telegram_opt_in: Mapped[bool] = mapped_column(Boolean, default=False)
    telegram_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    alert_preferences_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    company_profile: Mapped["CompanyProfile | None"] = relationship(back_populates="users")
    tender_states: Mapped[list["TenderState"]] = relationship(back_populates="user")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="user")


class TenderState(Base):
    __tablename__ = "tender_states"

    id: Mapped[int] = mapped_column(primary_key=True)
    tender_id: Mapped[int] = mapped_column(ForeignKey("tenders.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    state: Mapped[str] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    tender: Mapped["Tender"] = relationship(back_populates="states")
    user: Mapped["User"] = relationship(back_populates="tender_states")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    tender_id: Mapped[int] = mapped_column(ForeignKey("tenders.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    alert_type: Mapped[str] = mapped_column(String(50))
    scheduled_for: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivery_channel: Mapped[str] = mapped_column(String(50), default="dashboard")
    delivery_status: Mapped[str] = mapped_column(String(50), default="pending")
    delivery_attempts: Mapped[int] = mapped_column(default=0)
    last_error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payload_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    tender: Mapped["Tender"] = relationship(back_populates="alerts")
    user: Mapped["User"] = relationship(back_populates="alerts")


class AutomationSetting(Base):
    __tablename__ = "automation_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    ingestion_interval_hours: Mapped[int] = mapped_column(default=1)
    openai_api_key_override: Mapped[str | None] = mapped_column(Text, nullable=True)
    openai_model_override: Mapped[str | None] = mapped_column(String(100), nullable=True)
    llm_master_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_whatsapp_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    contact_telegram_handle: Mapped[str | None] = mapped_column(String(100), nullable=True)
    demo_booking_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    resend_api_key_override: Mapped[str | None] = mapped_column(Text, nullable=True)
    resend_from_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email_delivery_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    whatsapp_enabled_override: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    whatsapp_provider_override: Mapped[str | None] = mapped_column(String(50), nullable=True)
    whatsapp_meta_token_override: Mapped[str | None] = mapped_column(Text, nullable=True)
    whatsapp_meta_phone_number_id_override: Mapped[str | None] = mapped_column(String(255), nullable=True)
    whatsapp_meta_api_version_override: Mapped[str | None] = mapped_column(String(50), nullable=True)
    telegram_enabled_override: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    telegram_bot_token_override: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_run_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_run_finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_cycle_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
