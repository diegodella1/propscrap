from __future__ import annotations

from datetime import UTC, datetime

import httpx
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.tender import Alert, User
from app.services.alerts import list_dispatchable_alerts
from app.services.whatsapp import WhatsappMessage, get_whatsapp_provider


def dispatch_pending_alerts(db: Session) -> dict:
    settings = get_settings()
    provider = get_whatsapp_provider()
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
        if user is None or not user.whatsapp_number:
            _mark_failed(alert, "WhatsApp alert has no reachable user or number")
            failed += 1
            continue

        if not provider.is_available():
            alert.delivery_status = "blocked"
            alert.last_error_message = "WhatsApp provider not configured"
            blocked += 1
            continue

        try:
            result = provider.send_message(
                WhatsappMessage(
                    to_number=user.whatsapp_number,
                    body=_build_alert_message(alert, user),
                )
            )
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
