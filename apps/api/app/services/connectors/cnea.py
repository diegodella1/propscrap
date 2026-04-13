from __future__ import annotations

from collections.abc import Iterable

import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.connectors.comprar import ComprarConnector
from app.services.connectors.contratar import ContratarConnector
from app.services.http_safety import assert_public_https_url


class CneaConnector(BaseConnector):
    slug = "cnea"
    name = "CNEA"
    base_url = "https://www.argentina.gob.ar/cnea/transparencia/compras-y-contrataciones"
    official_page_url = "https://www.argentina.gob.ar/cnea/transparencia/compras-y-contrataciones"
    saf_marker = "servicio administrativo financiero 105"
    organization_markers = (
        "comisión nacional de energía atómica",
        "comision nacional de energia atomica",
        "cnea",
    )

    def fetch(self) -> list[RawTenderRecord]:
        self._assert_official_page_still_points_to_public_portals()

        items = self._filter_records(ComprarConnector().fetch())
        items.extend(self._filter_records(ContratarConnector().fetch()))
        if not items:
            raise ValueError("CNEA procurement records not found in COMPR.AR or CONTRAT.AR")
        return self._dedupe(items)

    def _assert_official_page_still_points_to_public_portals(self) -> None:
        assert_public_https_url(self.official_page_url, label="cnea.official_page_url")
        settings = get_settings()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.get(self.official_page_url)
            response.raise_for_status()
            html = response.text.lower()

        if self.saf_marker not in html or "compr.ar" not in html or "contrat.ar" not in html:
            raise ValueError("CNEA transparency page no longer references COMPR.AR/CONTRAT.AR for SAF 105")

    def _filter_records(self, records: Iterable[RawTenderRecord]) -> list[RawTenderRecord]:
        filtered: list[RawTenderRecord] = []
        for record in records:
            haystack = " ".join(
                part
                for part in (
                    record.organization,
                    record.title,
                    record.description_raw,
                    record.source_url,
                )
                if part
            ).lower()
            if self.saf_marker in haystack or any(marker in haystack for marker in self.organization_markers):
                filtered.append(record)
        return filtered

    @staticmethod
    def _dedupe(records: list[RawTenderRecord]) -> list[RawTenderRecord]:
        seen: set[tuple[str | None, str]] = set()
        items: list[RawTenderRecord] = []
        for record in records:
            key = (record.external_id, record.source_url)
            if key in seen:
                continue
            seen.add(key)
            items.append(record)
        return items
