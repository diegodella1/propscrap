from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.http_safety import assert_public_https_url


class IntaConnector(BaseConnector):
    slug = "inta"
    name = "INTA"
    base_url = "https://compras.inta.gob.ar"
    api_url = "https://sic.inta.gob.ar/api/public_tenders/"
    page_size = 100

    def fetch(self) -> list[RawTenderRecord]:
        assert_public_https_url(self.api_url, label="inta.api_url")
        settings = get_settings()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.get(
                self.api_url,
                params={"ordering": "-opening_date", "page_size": self.page_size},
            )
            response.raise_for_status()
            payload = response.json()
        return self._extract_records(payload)

    def _extract_records(self, payload: dict[str, Any]) -> list[RawTenderRecord]:
        rows = payload.get("results")
        if not isinstance(rows, list):
            raise ValueError("INTA procurement payload has invalid data shape")

        now = datetime.now(tz=UTC)
        items: list[RawTenderRecord] = []
        seen_ids: set[str] = set()
        for row in rows:
            if not isinstance(row, dict):
                continue

            opening_date = self._parse_datetime(row.get("opening_date"))
            if opening_date is None or opening_date < now:
                continue

            external_id = self._clean_text(str(row.get("internal_procedure") or ""))
            title = self._clean_text(str(row.get("tender_object") or ""))
            organization = self._clean_text(str(row.get("solicited_unit") or ""))
            procedure_type = self._clean_text(str(row.get("fk_tender_type") or ""))
            status_raw = self._clean_text(str(row.get("state_name") or ""))
            source_url = self._build_source_url(row.get("id"))
            detail_parts = [
                self._clean_text(str(row.get("categories") or "")),
                self._clean_text(str(row.get("opening_place") or "")),
            ]

            if not external_id or not title or external_id in seen_ids:
                continue
            seen_ids.add(external_id)

            items.append(
                RawTenderRecord(
                    external_id=external_id,
                    title=title,
                    description_raw=" | ".join(part for part in detail_parts if part) or None,
                    organization=organization or "INTA",
                    jurisdiction="Nación",
                    procedure_type=procedure_type or None,
                    publication_date=opening_date.date(),
                    deadline_date=self._parse_datetime(row.get("limit_date")) or opening_date,
                    opening_date=opening_date,
                    estimated_amount=None,
                    currency="ARS",
                    source_url=source_url,
                    status_raw=status_raw or "Apertura próxima",
                )
            )

        if not items:
            raise ValueError("INTA upcoming procurement records not found")

        return items

    @staticmethod
    def _parse_datetime(value: Any) -> datetime | None:
        if not value:
            return None
        try:
            parsed = datetime.fromisoformat(str(value))
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)

    @staticmethod
    def _clean_text(value: str) -> str:
        return " ".join(value.split()).strip()

    def _build_source_url(self, tender_id: Any) -> str:
        tender_id_str = self._clean_text(str(tender_id or ""))
        if not tender_id_str:
            return f"{self.base_url}/"
        return f"{self.base_url}/#/contrataciones/{tender_id_str}"
