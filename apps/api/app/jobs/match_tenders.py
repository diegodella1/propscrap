from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
import time

from sqlalchemy.exc import OperationalError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import SessionLocal, engine
from app.errors import NotFoundError, ValidationError
from app.models.tender import CompanyProfile, Tender, User
from app.services.company_profiles import (
    ensure_demo_company_profile,
    ensure_user_company_profile,
    get_company_profile,
    get_default_company_profile,
)
from app.services.documents import get_tender_with_documents
from app.services.matching import match_tender_to_company
from app.services.source_access import list_effective_source_ids_for_profile


@dataclass(slots=True)
class MatchBatchStats:
    matched_tenders: int = 0
    profiles_processed: int = 0
    retries: int = 0
    batches: int = 0


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

    allowed_source_ids = set(list_effective_source_ids_for_profile(db, profile))
    if allowed_source_ids and tender.source_id not in allowed_source_ids:
        raise ValidationError("Tender source is not enabled for this company profile")

    match = match_tender_to_company(db, tender, profile)
    db.commit()
    return {"tender_id": tender.id, "profile_id": profile.id, "score": str(match.score), "score_band": match.score_band}


def match_all_tenders(
    db: Session,
    profile_id: int | None = None,
    *,
    batch_size: int | None = None,
    max_retries: int | None = None,
) -> dict:
    settings = get_settings()
    batch_size = batch_size or settings.matching_batch_size
    max_retries = max_retries if max_retries is not None else settings.matching_max_retries

    if profile_id is not None:
        profiles = [resolve_profile(db, profile_id=profile_id)]
    else:
        profiles = db.execute(select(CompanyProfile).order_by(CompanyProfile.id.asc())).scalars().all()
        if not profiles:
            profiles = [ensure_demo_company_profile(db)]

    stats = MatchBatchStats()
    for profile in profiles:
        allowed_source_ids = list_effective_source_ids_for_profile(db, profile)
        if not allowed_source_ids:
            continue
        tender_ids = list(
            db.execute(select(Tender.id).where(Tender.source_id.in_(allowed_source_ids)).order_by(Tender.id.asc())).scalars().all()
        )
        _match_profile_tenders(
            profile.id,
            tender_ids,
            batch_size=batch_size,
            max_retries=max_retries,
            stats=stats,
        )
        stats.profiles_processed += 1
    return {
        "profile_id": profile_id,
        "matched_tenders": stats.matched_tenders,
        "profiles_processed": stats.profiles_processed,
        "batches": stats.batches,
        "retries": stats.retries,
        "batch_size": batch_size,
    }


def _chunked(values: list[int], size: int) -> Iterable[list[int]]:
    for index in range(0, len(values), size):
        yield values[index : index + size]


def _match_profile_tenders(
    profile_id: int,
    tender_ids: list[int],
    *,
    batch_size: int,
    max_retries: int,
    stats: MatchBatchStats,
) -> None:
    for tender_batch in _chunked(tender_ids, batch_size):
        attempts = 0
        while True:
            try:
                with SessionLocal() as batch_db:
                    profile = resolve_profile(batch_db, profile_id=profile_id)
                    for tender_id in tender_batch:
                        tender = get_tender_with_documents(batch_db, tender_id)
                        if tender is None:
                            continue
                        match_tender_to_company(batch_db, tender, profile)
                        stats.matched_tenders += 1
                    batch_db.commit()
                stats.batches += 1
                break
            except OperationalError:
                attempts += 1
                stats.retries += 1
                engine.dispose()
                if attempts > max_retries:
                    raise
                time.sleep(min(2 * attempts, 5))
