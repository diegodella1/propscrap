from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
import re
from typing import Any

import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.http_safety import assert_public_https_url


class CorrientesConnector(BaseConnector):
    slug = "licitaciones-corrientes"
    name = "Provincia de Corrientes"
    base_url = "https://www.cgpcorrientes.gov.ar"
    api_url = "https://nportal.cgpc.gob.ar/documentos/apiweb/generic?novedad=true"
    page_url = "https://www.cgpcorrientes.gov.ar/licitaciones-component"
    max_age_days = 120

    def fetch(self) -> list[RawTenderRecord]:
        assert_public_https_url(self.api_url, label="corrientes.api_url")
        settings = get_settings()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent, "Accept": "application/json"},
            follow_redirects=True,
            verify=False,
        ) as client:
            response = client.get(self.api_url)
            response.raise_for_status()
            payload = response.json()
        return self._extract_records(payload)

    def _extract_records(self, payload: Any) -> list[RawTenderRecord]:
        if not isinstance(payload, list):
            raise ValueError("Corrientes procurement payload has invalid data shape")

        items: list[RawTenderRecord] = []
        seen_ids: set[str] = set()
        for row in payload:
            if not isinstance(row, dict):
                continue
            if self._clean_text(str(row.get("seleccion") or "")).lower() != "licitaciones":
                continue

            title = self._clean_text(str(row.get("titulo") or ""))
            if not title or title.lower().startswith("pliego"):
                continue

            external_id = self._extract_external_id(title)
            if not external_id or external_id in seen_ids:
                continue
            seen_ids.add(external_id)

            organization = self._extract_organization(title)
            publication_date = self._parse_date(row.get("fecha_publicacion"))
            if not self._is_recent(publication_date):
                continue
            status_raw = self._clean_text(str(row.get("tipo_documento") or "")) or None
            description = self._clean_text(str(row.get("descripcion") or ""))

            items.append(
                RawTenderRecord(
                    external_id=external_id,
                    title=title,
                    description_raw=description or None,
                    organization=organization or None,
                    jurisdiction="Provincia de Corrientes",
                    procedure_type=self._extract_procedure_type(title),
                    publication_date=publication_date,
                    deadline_date=None,
                    opening_date=None,
                    estimated_amount=None,
                    currency="ARS",
                    source_url=self.page_url,
                    status_raw=status_raw,
                )
            )

        if not items:
            raise ValueError("Corrientes procurement records not found")
        return items

    def _is_recent(self, publication_date: date | None) -> bool:
        if publication_date is None:
            return False
        today = datetime.now(tz=UTC).date()
        return publication_date >= today - timedelta(days=self.max_age_days)

    def _extract_external_id(self, title: str) -> str:
        match = re.search(r"N[º°]?\s*([\d]+/\s*\d+)", title, re.IGNORECASE)
        if match is None:
            return ""
        return self._clean_text(match.group(1)).replace("/ ", "/")

    def _extract_procedure_type(self, title: str) -> str | None:
        upper_title = self._clean_text(title).upper()
        for procedure in ("LICITACIÓN PÚBLICA", "LICITACION PUBLICA", "LICITACIÓN PRIVADA", "LICITACION PRIVADA"):
            if procedure in upper_title:
                return procedure.title()
        return None

    def _extract_organization(self, title: str) -> str | None:
        parts = [self._clean_text(part) for part in re.split(r"\s*-\s*", title) if self._clean_text(part)]
        if len(parts) < 2:
            return None
        return parts[-1]

    @staticmethod
    def _parse_date(value: Any) -> date | None:
        raw = CorrientesConnector._clean_text(str(value or ""))
        if not raw:
            return None
        try:
            return date.fromisoformat(raw)
        except ValueError:
            return None

    @staticmethod
    def _clean_text(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()
