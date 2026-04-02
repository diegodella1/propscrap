from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.tender import Tender


def find_existing_tender(
    db: Session, source_id: int, external_id: str | None, dedupe_hash: str
) -> Tender | None:
    if external_id:
        by_external = db.execute(
            select(Tender).where(Tender.source_id == source_id, Tender.external_id == external_id)
        ).scalar_one_or_none()
        if by_external:
            return by_external

    by_hash = db.execute(select(Tender).where(Tender.dedupe_hash == dedupe_hash)).scalar_one_or_none()
    if by_hash:
        return by_hash

    return None


def apply_tender_updates(existing: Tender, candidate: Tender) -> Tender:
    existing.title = candidate.title
    existing.description_raw = candidate.description_raw
    existing.organization = candidate.organization
    existing.jurisdiction = candidate.jurisdiction
    existing.procedure_type = candidate.procedure_type
    existing.publication_date = candidate.publication_date
    existing.deadline_date = candidate.deadline_date
    existing.opening_date = candidate.opening_date
    existing.estimated_amount = candidate.estimated_amount
    existing.currency = candidate.currency
    existing.source_url = candidate.source_url
    existing.dedupe_hash = candidate.dedupe_hash
    existing.status_raw = candidate.status_raw
    return existing

