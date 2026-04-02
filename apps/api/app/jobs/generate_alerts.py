from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.tender import CompanyProfile
from app.services.alerts import generate_alerts
from app.services.company_profiles import ensure_demo_company_profile, get_default_company_profile
from app.services.users import ensure_demo_user, list_active_users


def run_alert_generation(db: Session) -> dict:
    ensure_demo_user(db)
    ensure_demo_company_profile(db)
    profile = get_default_company_profile(db)
    min_score = _resolve_min_score(profile)
    users = list_active_users(db)
    return generate_alerts(db, users, default_min_score=min_score)


def _resolve_min_score(profile: CompanyProfile | None) -> float:
    if profile is None or not profile.alert_preferences_json:
        return 60

    raw_value = profile.alert_preferences_json.get("min_score", 60)
    try:
        return float(raw_value)
    except (TypeError, ValueError):
        return 60
