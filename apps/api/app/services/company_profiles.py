from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.errors import ConflictError
from app.models.tender import CompanyProfile, User
from app.services.company_registry import CompanyLookupResult, validate_cuit

DEMO_PROFILE_NAME = "Tecnologia Sanitaria Integrada SA"
DEFAULT_PROFILE_DESCRIPTION = (
    "Empresa argentina que provee software, infraestructura IT, soporte, mantenimiento "
    "tecnológico, equipamiento médico conectado y servicios para organismos públicos y salud."
)
DEFAULT_SECTORS = ["software", "infraestructura IT", "salud", "equipamiento médico"]
DEFAULT_INCLUDE_KEYWORDS = [
    "software",
    "licencias",
    "mesa de ayuda",
    "infraestructura",
    "mantenimiento",
    "soporte",
    "hospital",
    "salud",
    "electromedicina",
    "equipos",
    "digitalización",
]
DEFAULT_EXCLUDE_KEYWORDS = [
    "balasto",
    "avícolas",
    "panificados",
    "textiles",
    "protesis",
    "cloruro",
    "ferroviarios",
]
DEFAULT_JURISDICTIONS = ["Nación", "Provincia de Buenos Aires"]
DEFAULT_BUYERS = [
    "Ministerio de Salud",
    "ANSES",
    "Hospital",
    "Instituto de Obra Social",
    "Ministerio de Defensa",
]
DEFAULT_COMPANY_ALERT_PREFERENCES = {
    "min_score": 60,
    "receive_relevant": True,
    "receive_deadlines": True,
    "deadline_only_for_saved": True,
    "deadline_offsets_hours": [168, 72, 24],
}


def normalize_company_alert_preferences(payload: dict | None) -> dict:
    if payload is None:
        return DEFAULT_COMPANY_ALERT_PREFERENCES.copy()
    if not isinstance(payload, dict):
        return DEFAULT_COMPANY_ALERT_PREFERENCES.copy()

    try:
        min_score = int(payload.get("min_score", DEFAULT_COMPANY_ALERT_PREFERENCES["min_score"]))
    except (TypeError, ValueError):
        min_score = DEFAULT_COMPANY_ALERT_PREFERENCES["min_score"]
    min_score = max(0, min(100, min_score))

    raw_offsets = payload.get("deadline_offsets_hours", DEFAULT_COMPANY_ALERT_PREFERENCES["deadline_offsets_hours"])
    normalized_offsets: list[int] = []
    if isinstance(raw_offsets, list):
        for value in raw_offsets:
            try:
                hours = int(value)
            except (TypeError, ValueError):
                continue
            if hours <= 0:
                continue
            if hours not in normalized_offsets:
                normalized_offsets.append(hours)
    normalized_offsets.sort(reverse=True)

    return {
        "min_score": min_score,
        "receive_relevant": bool(payload.get("receive_relevant", True)),
        "receive_deadlines": bool(payload.get("receive_deadlines", True)),
        "deadline_only_for_saved": bool(payload.get("deadline_only_for_saved", True)),
        "deadline_offsets_hours": normalized_offsets or DEFAULT_COMPANY_ALERT_PREFERENCES["deadline_offsets_hours"].copy(),
    }


def ensure_demo_company_profile(db: Session) -> CompanyProfile:
    existing = db.execute(
        select(CompanyProfile)
        .where(CompanyProfile.company_name == DEMO_PROFILE_NAME)
        .order_by(CompanyProfile.id.asc())
    ).scalars().first()
    if existing:
        return existing

    profile = CompanyProfile(
        company_name=DEMO_PROFILE_NAME,
        legal_name=DEMO_PROFILE_NAME,
        company_description=DEFAULT_PROFILE_DESCRIPTION,
        sectors=DEFAULT_SECTORS.copy(),
        include_keywords=DEFAULT_INCLUDE_KEYWORDS.copy(),
        exclude_keywords=DEFAULT_EXCLUDE_KEYWORDS.copy(),
        jurisdictions=DEFAULT_JURISDICTIONS.copy(),
        preferred_buyers=DEFAULT_BUYERS.copy(),
        min_amount=Decimal("1000000"),
        max_amount=Decimal("100000000"),
        alert_preferences_json=DEFAULT_COMPANY_ALERT_PREFERENCES.copy(),
    )
    db.add(profile)
    db.flush()
    return profile


def ensure_user_company_profile(db: Session, user: User) -> CompanyProfile:
    if user.company_profile_id:
        existing = get_company_profile(db, user.company_profile_id)
        if existing is not None:
            return existing

    desired_name = (user.company_name or user.full_name or "Mi empresa").strip()
    normalized_cuit = validate_cuit(user.cuit) if user.cuit else None
    if normalized_cuit:
        existing_by_cuit = db.execute(
            select(CompanyProfile).where(CompanyProfile.cuit == normalized_cuit)
        ).scalar_one_or_none()
        if existing_by_cuit is not None:
            user.company_profile_id = existing_by_cuit.id
            user.company_name = existing_by_cuit.company_name
            db.add(user)
            db.flush()
            return existing_by_cuit
    elif desired_name:
        existing_by_name = db.execute(
            select(CompanyProfile)
            .where(func.lower(CompanyProfile.company_name) == desired_name.lower())
            .order_by(CompanyProfile.id.asc())
        ).scalars().first()
        if existing_by_name is not None:
            user.company_profile_id = existing_by_name.id
            user.company_name = existing_by_name.company_name
            db.add(user)
            db.flush()
            return existing_by_name

    profile = CompanyProfile(
        cuit=normalized_cuit,
        company_name=desired_name,
        legal_name=desired_name,
        company_description=DEFAULT_PROFILE_DESCRIPTION,
        sectors=DEFAULT_SECTORS.copy(),
        include_keywords=DEFAULT_INCLUDE_KEYWORDS.copy(),
        exclude_keywords=DEFAULT_EXCLUDE_KEYWORDS.copy(),
        jurisdictions=DEFAULT_JURISDICTIONS.copy(),
        preferred_buyers=DEFAULT_BUYERS.copy(),
        min_amount=Decimal("1000000"),
        max_amount=Decimal("100000000"),
        alert_preferences_json=DEFAULT_COMPANY_ALERT_PREFERENCES.copy(),
    )
    db.add(profile)
    db.flush()
    user.company_profile_id = profile.id
    db.add(user)
    db.flush()
    return profile


def get_default_company_profile(db: Session) -> CompanyProfile | None:
    return db.execute(select(CompanyProfile).order_by(CompanyProfile.id.asc())).scalars().first()


def get_company_profile(db: Session, profile_id: int) -> CompanyProfile | None:
    return db.execute(select(CompanyProfile).where(CompanyProfile.id == profile_id)).scalar_one_or_none()


def get_company_profile_for_user(db: Session, user: User) -> CompanyProfile:
    return ensure_user_company_profile(db, user)


def list_company_profiles_with_users(db: Session) -> list[CompanyProfile]:
    return db.execute(select(CompanyProfile).order_by(CompanyProfile.id.asc())).scalars().all()


def update_company_profile(
    db: Session,
    profile: CompanyProfile,
    *,
    cuit: str | None,
    company_name: str,
    legal_name: str | None,
    company_description: str,
    sectors: list[str] | None,
    include_keywords: list[str] | None,
    exclude_keywords: list[str] | None,
    jurisdictions: list[str] | None,
    preferred_buyers: list[str] | None,
    min_amount: str | None,
    max_amount: str | None,
    alert_preferences_json: dict | None,
    tax_status_json: dict | None,
) -> CompanyProfile:
    normalized_cuit = validate_cuit(cuit) if cuit else None
    if normalized_cuit and normalized_cuit != profile.cuit:
        existing = db.execute(
            select(CompanyProfile).where(CompanyProfile.cuit == normalized_cuit, CompanyProfile.id != profile.id)
        ).scalar_one_or_none()
        if existing is not None:
            raise ConflictError(f"Ya existe un perfil de empresa para el CUIT {normalized_cuit}")
    profile.cuit = normalized_cuit
    profile.company_name = company_name.strip()
    profile.legal_name = legal_name.strip() if legal_name and legal_name.strip() else profile.company_name
    profile.company_description = company_description.strip()
    profile.sectors = sectors or []
    profile.include_keywords = include_keywords or []
    profile.exclude_keywords = exclude_keywords or []
    profile.jurisdictions = jurisdictions or []
    profile.preferred_buyers = preferred_buyers or []
    profile.min_amount = Decimal(min_amount) if min_amount else None
    profile.max_amount = Decimal(max_amount) if max_amount else None
    profile.alert_preferences_json = normalize_company_alert_preferences(alert_preferences_json)
    profile.tax_status_json = tax_status_json or profile.tax_status_json or {}
    db.add(profile)
    db.flush()
    return profile


def apply_company_lookup_result(
    db: Session,
    *,
    user: User,
    company_result: CompanyLookupResult,
) -> CompanyProfile:
    normalized_cuit = validate_cuit(company_result.cuit)
    existing = db.execute(select(CompanyProfile).where(CompanyProfile.cuit == normalized_cuit)).scalar_one_or_none()
    if existing is None:
        existing = CompanyProfile(
            cuit=normalized_cuit,
            company_name=company_result.company_name,
            legal_name=company_result.legal_name,
            company_description=DEFAULT_PROFILE_DESCRIPTION,
            sectors=company_result.sectors or DEFAULT_SECTORS.copy(),
            include_keywords=DEFAULT_INCLUDE_KEYWORDS.copy(),
            exclude_keywords=DEFAULT_EXCLUDE_KEYWORDS.copy(),
            jurisdictions=company_result.jurisdictions or DEFAULT_JURISDICTIONS.copy(),
            preferred_buyers=DEFAULT_BUYERS.copy(),
            min_amount=Decimal("1000000"),
            max_amount=Decimal("100000000"),
            alert_preferences_json=DEFAULT_COMPANY_ALERT_PREFERENCES.copy(),
            tax_status_json=company_result.tax_status_json,
            company_data_source=company_result.company_data_source,
            company_data_updated_at=company_result.company_data_updated_at,
        )
        db.add(existing)
        db.flush()
    else:
        existing.company_name = company_result.company_name
        existing.legal_name = company_result.legal_name
        if company_result.sectors:
            existing.sectors = company_result.sectors
        if company_result.jurisdictions:
            existing.jurisdictions = company_result.jurisdictions
        existing.tax_status_json = company_result.tax_status_json
        existing.company_data_source = company_result.company_data_source
        existing.company_data_updated_at = company_result.company_data_updated_at
        db.add(existing)
        db.flush()

    user.cuit = normalized_cuit
    user.company_name = existing.company_name
    user.company_profile_id = existing.id
    db.add(user)
    db.flush()
    return existing


def touch_company_profile_sync_metadata(
    db: Session,
    profile: CompanyProfile,
    *,
    company_data_source: str,
) -> CompanyProfile:
    profile.company_data_source = company_data_source
    profile.company_data_updated_at = datetime.now(tz=UTC)
    db.add(profile)
    db.flush()
    return profile
