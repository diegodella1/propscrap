from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import NotFoundError
from app.models.tender import CompanyProfile, Tender, User
from app.services.company_profiles import (
    ensure_demo_company_profile,
    ensure_user_company_profile,
    get_company_profile,
    get_default_company_profile,
)
from app.services.documents import get_tender_with_documents
from app.services.matching import match_tender_to_company


def resolve_profile(db: Session, profile_id: int | None = None):
    ensure_demo_company_profile(db)
    if profile_id is not None:
        profile = get_company_profile(db, profile_id)
        if profile is None:
            raise NotFoundError(f"Company profile not found: {profile_id}")
        return profile
    profile = get_default_company_profile(db)
    if profile is None:
        profile = ensure_demo_company_profile(db)
    return profile


def resolve_user_profile(db: Session, user: User) -> CompanyProfile:
    return ensure_user_company_profile(db, user)


def match_tender(db: Session, tender_id: int, profile_id: int | None = None) -> dict:
    profile = resolve_profile(db, profile_id=profile_id)
    tender = get_tender_with_documents(db, tender_id)
    if tender is None:
        raise NotFoundError(f"Tender not found: {tender_id}")

    match = match_tender_to_company(db, tender, profile)
    db.commit()
    return {"tender_id": tender.id, "profile_id": profile.id, "score": str(match.score), "score_band": match.score_band}


def match_all_tenders(db: Session, profile_id: int | None = None) -> dict:
    tenders = db.execute(select(Tender.id).order_by(Tender.id.asc())).all()
    if profile_id is not None:
        profiles = [resolve_profile(db, profile_id=profile_id)]
    else:
        profiles = db.execute(select(CompanyProfile).order_by(CompanyProfile.id.asc())).scalars().all()
        if not profiles:
            profiles = [ensure_demo_company_profile(db)]

    matched = 0
    for profile in profiles:
        for (tender_id,) in tenders:
            tender = get_tender_with_documents(db, tender_id)
            if tender is None:
                continue
            match_tender_to_company(db, tender, profile)
            matched += 1
    db.commit()
    return {"profile_id": profile_id, "matched_tenders": matched, "profiles_processed": len(profiles)}
