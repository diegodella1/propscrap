from __future__ import annotations

from hashlib import sha256

from app.models.tender import Tender
from app.services.connectors.base import RawTenderRecord


def build_dedupe_hash(record: RawTenderRecord) -> str:
    key_parts = [
        (record.title or "").strip().lower(),
        (record.organization or "").strip().lower(),
        record.publication_date.isoformat() if record.publication_date else "",
        (record.procedure_type or "").strip().lower(),
    ]
    return sha256("|".join(key_parts).encode("utf-8")).hexdigest()


def normalize_tender(source_id: int, record: RawTenderRecord) -> Tender:
    return Tender(
        source_id=source_id,
        external_id=record.external_id,
        title=record.title,
        description_raw=record.description_raw,
        organization=record.organization,
        jurisdiction=record.jurisdiction,
        procedure_type=record.procedure_type,
        publication_date=record.publication_date,
        deadline_date=record.deadline_date,
        opening_date=record.opening_date,
        estimated_amount=record.estimated_amount,
        currency=record.currency,
        source_url=record.source_url,
        dedupe_hash=build_dedupe_hash(record),
        status_raw=record.status_raw,
    )

