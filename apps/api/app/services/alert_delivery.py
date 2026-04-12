from __future__ import annotations

from datetime import UTC, datetime

import httpx
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.tender import Alert, User
from app.services.email import EmailMessage, NullEmailProvider, ResendEmailProvider
from app.services.alerts import list_dispatchable_alerts
from app.services.runtime_settings import get_automation_settings
from app.services.whatsapp import WhatsappMessage, get_whatsapp_provider


def dispatch_pending_alerts(db: Session) -> dict:
    settings = get_settings()
    runtime_settings = get_automation_settings(db)
    whatsapp_provider = get_whatsapp_provider()
    email_provider = _build_email_provider(runtime_settings)
    alerts = list_dispatchable_alerts(db, limit=settings.alert_dispatch_batch_size)

    if not alerts:
        return {"processed": 0, "sent": 0, "blocked": 0, "failed": 0}

    processed = 0
    sent = 0
    blocked = 0
    failed = 0

    for alert in alerts:
        processed += 1
        user = alert.user
        try:
            result = _dispatch_alert(
                alert,
                user,
                whatsapp_provider=whatsapp_provider,
                email_provider=email_provider,
            )
        except RuntimeError as exc:
            alert.delivery_status = "blocked"
            alert.last_error_message = str(exc)[:500]
            blocked += 1
            continue
        except httpx.HTTPError as exc:
            _mark_retry_or_failed(alert, str(exc), max_attempts=settings.alert_dispatch_max_attempts)
            failed += 1
            continue
        except Exception as exc:
            _mark_retry_or_failed(alert, str(exc), max_attempts=settings.alert_dispatch_max_attempts)
            failed += 1
            continue

        alert.delivery_status = "sent"
        alert.sent_at = datetime.now(tz=UTC)
        alert.delivery_attempts += 1
        alert.last_error_message = None
        alert.provider_message_id = result.provider_message_id
        sent += 1

    db.commit()
    return {"processed": processed, "sent": sent, "blocked": blocked, "failed": failed}


def _dispatch_alert(
    alert: Alert,
    user: User | None,
    *,
    whatsapp_provider,
    email_provider,
):
    if alert.delivery_channel == "whatsapp":
        if user is None or not user.whatsapp_number:
            raise RuntimeError("WhatsApp alert has no reachable user or number")
        if not whatsapp_provider.is_available():
            raise RuntimeError("WhatsApp provider not configured")
        return whatsapp_provider.send_message(
            WhatsappMessage(
                to_number=user.whatsapp_number,
                body=_build_alert_message(alert, user),
            )
        )

    if alert.delivery_channel == "email":
        if user is None or not user.email:
            raise RuntimeError("Email alert has no reachable user or email")
        if not email_provider.is_available():
            raise RuntimeError("Email provider not configured")
        subject, html, text = _build_email_alert_message(alert, user)
        return email_provider.send_message(
            EmailMessage(
                to_email=user.email,
                subject=subject,
                html=html,
                text=text,
            )
        )

    raise RuntimeError(f"Unsupported delivery channel: {alert.delivery_channel}")


def _build_alert_message(alert: Alert, user: User) -> str:
    title = (alert.payload_snapshot or {}).get("title") or f"Tender #{alert.tender_id}"
    if alert.alert_type == "new_relevant":
        score = (alert.payload_snapshot or {}).get("score", "n/d")
        return (
            f"{user.full_name}, nueva licitacion relevante.\n"
            f"{title}\n"
            f"Score: {score}\n"
            f"Revisa el dashboard para decidir el siguiente paso."
        )

    deadline = (alert.payload_snapshot or {}).get("deadline_date", "sin fecha")
    return (
        f"{user.full_name}, recordatorio de licitacion.\n"
        f"{title}\n"
        f"Alerta: {alert.alert_type}\n"
        f"Deadline: {deadline}"
    )


def _build_email_alert_message(alert: Alert, user: User) -> tuple[str, str, str]:
    title = (alert.payload_snapshot or {}).get("title") or f"Tender #{alert.tender_id}"
    if alert.alert_type == "new_relevant":
        score = (alert.payload_snapshot or {}).get("score", "n/d")
        subject = f"Nueva licitacion relevante: {title}"
        text = (
            f"{user.full_name}, se detecto una nueva licitacion relevante.\n\n"
            f"{title}\n"
            f"Score: {score}\n"
            "Revisala en EasyTaciones para decidir el siguiente paso."
        )
    else:
        deadline = (alert.payload_snapshot or {}).get("deadline_date", "sin fecha")
        subject = f"Recordatorio de licitacion: {title}"
        text = (
            f"{user.full_name}, tenes un recordatorio de licitacion.\n\n"
            f"{title}\n"
            f"Alerta: {alert.alert_type}\n"
            f"Deadline: {deadline}"
        )

    html = text.replace("\n", "<br />")
    return subject, html, text


def _build_email_provider(runtime_settings) -> ResendEmailProvider | NullEmailProvider:
    settings = get_settings()
    if not runtime_settings.email_delivery_enabled:
        return NullEmailProvider()

    api_key = runtime_settings.resend_api_key_override or settings.resend_api_key
    from_email = runtime_settings.resend_from_email or settings.resend_from_email
    provider = ResendEmailProvider(api_key=api_key, from_email=from_email)
    if provider.is_available():
        return provider
    return NullEmailProvider()


def _mark_retry_or_failed(alert: Alert, error_message: str, *, max_attempts: int) -> None:
    alert.delivery_attempts += 1
    alert.last_error_message = error_message[:500]
    if alert.delivery_attempts >= max_attempts:
        alert.delivery_status = "failed"
    else:
        alert.delivery_status = "retrying"


def _mark_failed(alert: Alert, error_message: str) -> None:
    alert.delivery_attempts += 1
    alert.delivery_status = "failed"
    alert.last_error_message = error_message[:500]
