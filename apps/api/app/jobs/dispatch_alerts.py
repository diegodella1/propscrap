from __future__ import annotations

from sqlalchemy.orm import Session

from app.services.alert_delivery import dispatch_pending_alerts


def run_alert_dispatch(db: Session) -> dict:
    return dispatch_pending_alerts(db)
