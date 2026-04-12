from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class SourceRead(BaseModel):
    id: int
    name: str
    slug: str
    source_type: str
    base_url: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class SourceRunRead(BaseModel):
    id: int
    source_id: int
    status: str
    started_at: datetime
    finished_at: datetime | None = None
    items_found: int
    items_new: int
    error_message: str | None = None

    model_config = ConfigDict(from_attributes=True)


class DocumentTextRead(BaseModel):
    id: int
    extraction_method: str
    extraction_status: str
    extracted_text: str | None = None
    text_length: int
    confidence_score: Decimal | None = None

    model_config = ConfigDict(from_attributes=True)


class TenderDocumentRead(BaseModel):
    id: int
    document_type: str
    filename: str
    file_path: str | None = None
    source_url: str
    download_status: str
    downloaded_at: datetime | None = None
    texts: list[DocumentTextRead] = []

    model_config = ConfigDict(from_attributes=True)


class TenderEnrichmentRead(BaseModel):
    id: int
    llm_model: str | None = None
    summary_short: str | None = None
    summary_structured_json: dict | None = None
    key_requirements: list | None = None
    risk_flags: list | None = None
    extracted_deadlines: dict | None = None
    enrichment_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TenderMatchRead(BaseModel):
    id: int
    company_profile_id: int
    score: Decimal
    score_band: str
    reasons_json: dict | None = None
    matched_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TenderStateRead(BaseModel):
    id: int
    user_id: int
    state: str
    notes: str | None = None
    alert_overrides_json: dict | None = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertRead(BaseModel):
    id: int
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


class TenderRead(BaseModel):
    id: int
    source_id: int
    external_id: str | None = None
    title: str
    description_raw: str | None = None
    organization: str | None = None
    jurisdiction: str | None = None
    procedure_type: str | None = None
    publication_date: date | None = None
    deadline_date: datetime | None = None
    opening_date: datetime | None = None
    estimated_amount: Decimal | None = None
    currency: str | None = None
    source_url: str
    status_raw: str | None = None
    source: SourceRead
    matches: list[TenderMatchRead] = []
    states: list[TenderStateRead] = []

    model_config = ConfigDict(from_attributes=True)


class TenderDetailRead(TenderRead):
    detail_html_path: str | None = None
    detail_cached_at: datetime | None = None
    documents: list[TenderDocumentRead] = []
    enrichments: list[TenderEnrichmentRead] = []
    alerts: list[AlertRead] = []


class TenderListResponse(BaseModel):
    items: list[TenderRead]
    total: int
