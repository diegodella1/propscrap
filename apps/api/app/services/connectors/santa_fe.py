from __future__ import annotations

from datetime import UTC, datetime
import re

import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.http_safety import assert_public_https_url


class SantaFeConnector(BaseConnector):
    slug = "licitaciones-santa-fe"
    name = "Provincia de Santa Fe"
    base_url = "https://www.santafe.gov.ar"
    page_url = "https://www.santafe.gov.ar/gestionesdecompras/site/index.php?a=consultas.index"
    ajax_url = "https://www.santafe.gov.ar/gestionesdecompras/site/AppAjax.php"
    page_size = 100

    def fetch(self) -> list[RawTenderRecord]:
        assert_public_https_url(self.ajax_url, label="santa_fe.ajax_url")
        settings = get_settings()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            current_year = datetime.now(tz=UTC).year
            items: list[RawTenderRecord] = []
            seen_ids: set[str] = set()
            start = 0
            total_records: int | None = None

            while total_records is None or start < total_records:
                payload = self._fetch_page(client=client, year=current_year, start=start, limit=self.page_size)
                page_items = self._extract_records(payload)
                if not page_items:
                    break

                for item in page_items:
                    dedupe_key = item.external_id or item.source_url
                    if dedupe_key in seen_ids:
                        continue
                    seen_ids.add(dedupe_key)
                    items.append(item)

                total_records = self._parse_total_records(payload)
                start += self.page_size

        if not items:
            raise ValueError("Santa Fe procurement records not found")
        return items

    def _fetch_page(self, *, client: httpx.Client, year: int, start: int, limit: int) -> dict:
        response = client.post(
            self.ajax_url,
            params={"a": "consultas.getContrataciones", "anio": year},
            data={"estado": "AP", "start": start, "limit": limit},
        )
        response.raise_for_status()
        payload = response.json()
        if not payload.get("success"):
            reason = payload.get("errors", {}).get("reason") or "unknown error"
            raise ValueError(f"Santa Fe Ajax query failed: {reason}")
        return payload

    def _extract_records(self, payload: dict) -> list[RawTenderRecord]:
        rows = payload.get("data")
        if not isinstance(rows, list):
            raise ValueError("Santa Fe procurement payload has invalid data shape")
        items: list[RawTenderRecord] = []
        for row in rows:
            if not isinstance(row, dict):
                continue

            opening_date = self._parse_datetime(str(row.get("fechaHoraAperturaFija") or row.get("fechaHoraApertura") or ""))
            procedure_type = self._clean_text(str(row.get("tipoGestion") or ""))
            procedure_mode = self._clean_text(str(row.get("tipoModalidad") or ""))
            title = self._clean_text(str(row.get("objeto") or row.get("objetoCompleto") or ""))
            description = self._clean_text(str(row.get("objetoCompleto") or title))
            organization = self._clean_text(str(row.get("comprador") or ""))
            external_id = self._extract_external_id(row)
            source_url = self._build_source_url(str(row.get("idGestion") or ""))
            status_raw = self._clean_text(str(row.get("estado") or "Apertura"))

            if not external_id or not title:
                continue

            items.append(
                RawTenderRecord(
                    external_id=external_id,
                    title=title,
                    description_raw=description or None,
                    organization=organization or None,
                    jurisdiction="Provincia de Santa Fe",
                    procedure_type=self._join_non_empty([procedure_type, procedure_mode]) or None,
                    publication_date=opening_date.date() if opening_date else None,
                    deadline_date=opening_date,
                    opening_date=opening_date,
                    estimated_amount=None,
                    currency="ARS",
                    source_url=source_url,
                    status_raw=status_raw,
                )
            )

        return items

    @staticmethod
    def _parse_total_records(payload: dict) -> int | None:
        raw_total = payload.get("totalRecords")
        try:
            return int(str(raw_total))
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        raw = value.strip()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%d-%m-%Y %H:%M"):
            try:
                return datetime.strptime(raw, fmt).replace(tzinfo=UTC)
            except ValueError:
                continue
        return None

    @staticmethod
    def _extract_external_id(row: dict) -> str:
        numero_ano = SantaFeConnector._clean_text(str(row.get("numeroAño") or ""))
        if numero_ano:
            return numero_ano.replace("-", "/")
        match = re.search(r"(\d+)[-/](\d{4})", str(row.get("tipoGestion") or ""))
        if match:
            return f"{match.group(1)}/{match.group(2)}"
        id_gestion = SantaFeConnector._clean_text(str(row.get("idGestion") or ""))
        if id_gestion:
            return id_gestion
        return ""

    @staticmethod
    def _clean_text(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()

    def _build_source_url(self, id_gestion: str) -> str:
        if not id_gestion:
            return self.page_url
        return f"{self.base_url}/gestionesdecompras/site/gestion.php?idGestion={id_gestion}&contar=1"

    @staticmethod
    def _join_non_empty(parts: list[str]) -> str:
        return " | ".join(part for part in parts if part)
