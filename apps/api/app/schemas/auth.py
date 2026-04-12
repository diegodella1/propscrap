from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.schemas.admin import UserRead


class SignupRequest(BaseModel):
    full_name: str
    email: str
    password: str
    cuit: str
    company_name: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class MeUpdateRequest(BaseModel):
    full_name: str | None = None
    company_name: str | None = None
    cuit: str | None = None
    whatsapp_number: str | None = None
    whatsapp_opt_in: bool | None = None
    telegram_chat_id: str | None = None
    telegram_opt_in: bool | None = None
    email_opt_in: bool | None = None
    telegram_opt_in_alerts: bool | None = None
    alert_priority: str | None = None
    receive_deadlines: bool | None = None
    receive_relevant: bool | None = None


class CompanyLookupRead(BaseModel):
    cuit: str
    company_name: str
    legal_name: str
    tax_status_json: dict | None = None
    company_data_source: str
    company_data_updated_at: datetime
    jurisdictions: list[str] | None = None
    sectors: list[str] | None = None


class AuthResponse(BaseModel):
    user: UserRead
