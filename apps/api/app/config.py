from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Licitaciones IA API"
    env: str = Field(default="development", alias="LIA_ENV")
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:54329/licitaciones_ia",
        alias="DATABASE_URL",
    )
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    cors_origins: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")
    connector_timeout_seconds: int = Field(default=30, alias="CONNECTOR_TIMEOUT_SECONDS")
    user_agent: str = Field(default="LicitacionesIA-POC/0.1", alias="USER_AGENT")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")
    llm_enabled: bool = Field(default=True, alias="LLM_ENABLED")
    llm_enrichment_batch_size: int = Field(default=10, alias="LLM_ENRICHMENT_BATCH_SIZE")
    arca_padron_archive_url: str = Field(
        default="https://www.afip.gob.ar/genericos/cInscripcion/archivos/apellidoNombreDenominacion.zip",
        alias="ARCA_PADRON_ARCHIVE_URL",
    )
    arca_padron_cache_hours: int = Field(default=24 * 7, alias="ARCA_PADRON_CACHE_HOURS")
    arca_ws_constancia_url: str = Field(
        default="https://aws.arca.gob.ar/sr-padron/webservices/personaServiceA5",
        alias="ARCA_WS_CONSTANCIA_URL",
    )
    arca_ws_token: str | None = Field(default=None, alias="ARCA_WS_TOKEN")
    arca_ws_sign: str | None = Field(default=None, alias="ARCA_WS_SIGN")
    arca_ws_cuit_representada: str | None = Field(default=None, alias="ARCA_WS_CUIT_REPRESENTADA")
    whatsapp_provider: str = Field(default="mock", alias="WHATSAPP_PROVIDER")
    whatsapp_enabled: bool = Field(default=False, alias="WHATSAPP_ENABLED")
    whatsapp_meta_token: str | None = Field(default=None, alias="WHATSAPP_META_TOKEN")
    whatsapp_meta_phone_number_id: str | None = Field(default=None, alias="WHATSAPP_META_PHONE_NUMBER_ID")
    whatsapp_meta_api_version: str = Field(default="v23.0", alias="WHATSAPP_META_API_VERSION")
    whatsapp_outbox_path: str = Field(
        default="data/outbox/whatsapp_messages.jsonl",
        alias="WHATSAPP_OUTBOX_PATH",
    )
    resend_api_key: str | None = Field(default=None, alias="RESEND_API_KEY")
    resend_from_email: str | None = Field(default=None, alias="RESEND_FROM_EMAIL")
    alert_dispatch_batch_size: int = Field(default=50, alias="ALERT_DISPATCH_BATCH_SIZE")
    alert_dispatch_max_attempts: int = Field(default=5, alias="ALERT_DISPATCH_MAX_ATTEMPTS")
    automation_poll_seconds: int = Field(default=60, alias="AUTOMATION_POLL_SECONDS")
    session_secret: str = Field(default="change-me-in-production", alias="SESSION_SECRET")
    session_cookie_name: str = Field(default="propscrap_session", alias="SESSION_COOKIE_NAME")
    session_max_age_seconds: int = Field(default=60 * 60 * 24 * 14, alias="SESSION_MAX_AGE_SECONDS")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
