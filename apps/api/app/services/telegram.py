from __future__ import annotations

from dataclasses import dataclass
import uuid

import httpx


@dataclass(slots=True)
class TelegramMessage:
    chat_id: str
    text: str


@dataclass(slots=True)
class TelegramSendResult:
    provider_message_id: str
    provider_name: str


class TelegramProvider:
    provider_name = "telegram"

    def is_available(self) -> bool:
        raise NotImplementedError

    def send_message(self, message: TelegramMessage) -> TelegramSendResult:
        raise NotImplementedError


class NullTelegramProvider(TelegramProvider):
    def is_available(self) -> bool:
        return False

    def send_message(self, message: TelegramMessage) -> TelegramSendResult:
        raise RuntimeError("Telegram provider not configured")


class BotTelegramProvider(TelegramProvider):
    def __init__(self, *, bot_token: str | None) -> None:
        self.bot_token = bot_token

    def is_available(self) -> bool:
        return bool(self.bot_token)

    def send_message(self, message: TelegramMessage) -> TelegramSendResult:
        if not self.is_available():
            raise RuntimeError("Telegram provider not configured")

        response = httpx.post(
            f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
            json={
                "chat_id": message.chat_id,
                "text": message.text,
                "disable_web_page_preview": True,
            },
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        provider_message_id = str((payload.get("result") or {}).get("message_id") or f"telegram-{uuid.uuid4()}")
        return TelegramSendResult(provider_message_id=provider_message_id, provider_name=self.provider_name)
