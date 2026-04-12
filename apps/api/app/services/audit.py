from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.admin_audit import AdminAuditEvent


def record_admin_audit(
    db: Session,
    *,
    actor_user_id: int,
    action: str,
    detail: dict[str, Any] | None = None,
) -> None:
    row = AdminAuditEvent(actor_user_id=actor_user_id, action=action, detail_json=detail or {})
    db.add(row)
