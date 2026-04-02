from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
import uuid

import httpx

from app.config import get_settings


@dataclass(slots=True)
class WhatsappMessage:
    to_number: str
    body: str


@dataclass(slots=True)
class WhatsappSendResult:
    provider_message_id: str
    provider_name: str


class WhatsappProvider:
    provider_name = "base"

    def is_available(self) -> bool:
        raise NotImplementedError

    def send_message(self, message: WhatsappMessage) -> WhatsappSendResult:
        raise NotImplementedError


class MockWhatsappProvider(WhatsappProvider):
    provider_name = "mock"

    def __init__(self, outbox_path: Path) -> None:
        self.outbox_path = outbox_path

    def is_available(self) -> bool:
        return True

    def send_message(self, message: WhatsappMessage) -> WhatsappSendResult:
        self.outbox_path.parent.mkdir(parents=True, exist_ok=True)
        provider_message_id = f"mock-{uuid.uuid4()}"
        record = {
            "id": provider_message_id,
            "provider": self.provider_name,
            "to": message.to_number,
            "body": message.body,
            "created_at": datetime.now(tz=UTC).isoformat(),
        }
        with self.outbox_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=True))
            handle.write("\n")
        return WhatsappSendResult(provider_message_id=provider_message_id, provider_name=self.provider_name)


class MetaWhatsappProvider(WhatsappProvider):
    provider_name = "meta"

    def __init__(self, *, api_version: str, token: str | None, phone_number_id: str | None) -> None:
        self.api_version = api_version
        self.token = token
        self.phone_number_id = phone_number_id

    def is_available(self) -> bool:
        return bool(self.token and self.phone_number_id)

    def send_message(self, message: WhatsappMessage) -> WhatsappSendResult:
        payload = {
            "messaging_product": "whatsapp",
            "to": message.to_number,
            "type": "text",
            "text": {"preview_url": False, "body": message.body},
        }
        with httpx.Client(
            base_url=f"https://graph.facebook.com/{self.api_version}",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            timeout=30,
        ) as client:
            response = client.post(f"/{self.phone_number_id}/messages", json=payload)
            response.raise_for_status()
            data = response.json()

        provider_message_id = ((data.get("messages") or [{}])[0]).get("id") or f"meta-{uuid.uuid4()}"
        return WhatsappSendResult(provider_message_id=provider_message_id, provider_name=self.provider_name)


def get_whatsapp_provider() -> WhatsappProvider:
    settings = get_settings()
    configured_outbox_path = Path(settings.whatsapp_outbox_path)
    outbox_path = (
        configured_outbox_path
        if configured_outbox_path.is_absolute()
        else Path(__file__).resolve().parents[4] / configured_outbox_path
    )

    if not settings.whatsapp_enabled:
        return MetaWhatsappProvider(api_version=settings.whatsapp_meta_api_version, token=None, phone_number_id=None)

    if settings.whatsapp_provider == "meta":
        return MetaWhatsappProvider(
            api_version=settings.whatsapp_meta_api_version,
            token=settings.whatsapp_meta_token,
            phone_number_id=settings.whatsapp_meta_phone_number_id,
        )

    return MockWhatsappProvider(outbox_path=outbox_path)
