from __future__ import annotations

from pydantic import BaseModel

from app.schemas.admin import UserRead


class SignupRequest(BaseModel):
    full_name: str
    email: str
    password: str
    company_name: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class MeUpdateRequest(BaseModel):
    full_name: str | None = None
    company_name: str | None = None
    whatsapp_number: str | None = None
    whatsapp_opt_in: bool | None = None
    alert_priority: str | None = None
    receive_deadlines: bool | None = None
    receive_relevant: bool | None = None


class AuthResponse(BaseModel):
    user: UserRead
