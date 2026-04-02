from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tender import CompanyProfile, User

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


def ensure_demo_company_profile(db: Session) -> CompanyProfile:
    existing = db.execute(
        select(CompanyProfile).where(CompanyProfile.company_name == DEMO_PROFILE_NAME)
    ).scalar_one_or_none()
    if existing:
        return existing

    profile = CompanyProfile(
        company_name=DEMO_PROFILE_NAME,
        company_description=DEFAULT_PROFILE_DESCRIPTION,
        sectors=DEFAULT_SECTORS.copy(),
        include_keywords=DEFAULT_INCLUDE_KEYWORDS.copy(),
        exclude_keywords=DEFAULT_EXCLUDE_KEYWORDS.copy(),
        jurisdictions=DEFAULT_JURISDICTIONS.copy(),
        preferred_buyers=DEFAULT_BUYERS.copy(),
        min_amount=Decimal("1000000"),
        max_amount=Decimal("100000000"),
        alert_preferences_json={"min_score": 60},
    )
    db.add(profile)
    db.flush()
    return profile


def ensure_user_company_profile(db: Session, user: User) -> CompanyProfile:
    if user.company_profile_id:
        existing = get_company_profile(db, user.company_profile_id)
        if existing is not None:
            return existing

    profile = CompanyProfile(
        company_name=(user.company_name or user.full_name or "Mi empresa").strip(),
        company_description=DEFAULT_PROFILE_DESCRIPTION,
        sectors=DEFAULT_SECTORS.copy(),
        include_keywords=DEFAULT_INCLUDE_KEYWORDS.copy(),
        exclude_keywords=DEFAULT_EXCLUDE_KEYWORDS.copy(),
        jurisdictions=DEFAULT_JURISDICTIONS.copy(),
        preferred_buyers=DEFAULT_BUYERS.copy(),
        min_amount=Decimal("1000000"),
        max_amount=Decimal("100000000"),
        alert_preferences_json={"min_score": 60},
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
    company_name: str,
    company_description: str,
    sectors: list[str] | None,
    include_keywords: list[str] | None,
    exclude_keywords: list[str] | None,
    jurisdictions: list[str] | None,
    preferred_buyers: list[str] | None,
    min_amount: str | None,
    max_amount: str | None,
    alert_preferences_json: dict | None,
) -> CompanyProfile:
    profile.company_name = company_name.strip()
    profile.company_description = company_description.strip()
    profile.sectors = sectors or []
    profile.include_keywords = include_keywords or []
    profile.exclude_keywords = exclude_keywords or []
    profile.jurisdictions = jurisdictions or []
    profile.preferred_buyers = preferred_buyers or []
    profile.min_amount = Decimal(min_amount) if min_amount else None
    profile.max_amount = Decimal(max_amount) if max_amount else None
    profile.alert_preferences_json = alert_preferences_json or {}
    db.add(profile)
    db.flush()
    return profile
