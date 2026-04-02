from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass(slots=True)
class RawTenderRecord:
    external_id: str | None
    title: str
    description_raw: str | None
    organization: str | None
    jurisdiction: str | None
    procedure_type: str | None
    publication_date: date | None
    deadline_date: datetime | None
    opening_date: datetime | None
    estimated_amount: Decimal | None
    currency: str | None
    source_url: str
    status_raw: str | None


class BaseConnector:
    slug: str
    name: str
    base_url: str

    def fetch(self) -> list[RawTenderRecord]:
        raise NotImplementedError

    def fetch_detail_html(self, source_url: str) -> str | None:
        return None
