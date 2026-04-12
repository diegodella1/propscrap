from __future__ import annotations

from dataclasses import dataclass

import httpx


@dataclass
class EmailMessage:
    to_email: str
    subject: str
    html: str
    text: str


@dataclass
class EmailSendResult:
    provider_message_id: str | None


class EmailProvider:
    def is_available(self) -> bool:
        raise NotImplementedError

    def send_message(self, message: EmailMessage) -> EmailSendResult:
        raise NotImplementedError


class NullEmailProvider(EmailProvider):
    def is_available(self) -> bool:
        return False

    def send_message(self, message: EmailMessage) -> EmailSendResult:
        raise RuntimeError("Email provider not configured")


class ResendEmailProvider(EmailProvider):
    def __init__(self, *, api_key: str | None, from_email: str | None) -> None:
        self.api_key = api_key
        self.from_email = from_email

    def is_available(self) -> bool:
        return bool(self.api_key and self.from_email)

    def send_message(self, message: EmailMessage) -> EmailSendResult:
        if not self.is_available():
            raise RuntimeError("Resend provider not configured")

        response = httpx.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": self.from_email,
                "to": [message.to_email],
                "subject": message.subject,
                "html": message.html,
                "text": message.text,
            },
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        return EmailSendResult(provider_message_id=payload.get("id"))
