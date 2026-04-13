from __future__ import annotations

from datetime import UTC, datetime
import re

from bs4 import BeautifulSoup
import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.http_safety import assert_public_https_url


class SaltaConnector(BaseConnector):
    slug = "licitaciones-salta"
    name = "Provincia de Salta"
    base_url = "https://compras.salta.gob.ar"
    search_url = "https://compras.salta.gob.ar/publico/publicacionactual/panelfiltrobusqueda/250"

    def fetch(self) -> list[RawTenderRecord]:
        assert_public_https_url(self.search_url, label="salta.search_url")
        settings = get_settings()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.get(self.search_url)
            response.raise_for_status()
            html = response.text
        return self._extract_records(html)

    def _extract_records(self, html: str) -> list[RawTenderRecord]:
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text("\n", strip=True)
        normalized = re.sub(r"\n{2,}", "\n", text)
        pattern = re.compile(
            r"Fecha/Hora Apertura:\s*(?P<opening>\d{2}/\d{2}/\d{4}\s*-\s*\d{2}:\d{2})\s+"
            r"(?P<procedure>(?:Licitación|Adjudicación|Contratación)[^\n]+)\s+"
            r"Objeto:\s*(?P<object>[^\n]+)\s+"
            r"Organismo Originante y Destino:\s*(?P<organization>[^\n]+)\s+"
            r"Expte\.\s*:\s*(?P<expediente>[^\n]+)",
            re.IGNORECASE,
        )

        items: list[RawTenderRecord] = []
        for match in pattern.finditer(normalized):
            opening_date = self._parse_datetime(match.group("opening"))
            procedure = self._clean_text(match.group("procedure"))
            expediente = self._clean_text(match.group("expediente"))
            title = self._clean_text(match.group("object"))
            organization = self._clean_text(match.group("organization"))
            external_id = expediente or procedure
            items.append(
                RawTenderRecord(
                    external_id=external_id,
                    title=title,
                    description_raw=f"{procedure}. {organization}",
                    organization=organization,
                    jurisdiction="Provincia de Salta",
                    procedure_type=self._extract_procedure_type(procedure),
                    publication_date=opening_date.date() if opening_date else None,
                    deadline_date=opening_date,
                    opening_date=opening_date,
                    estimated_amount=None,
                    currency="ARS",
                    source_url=self.search_url,
                    status_raw=procedure,
                )
            )

        if not items:
            raise ValueError("Salta public listing blocks not found")

        return items

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.strptime(value.strip(), "%d/%m/%Y - %H:%M").replace(tzinfo=UTC)
        except ValueError:
            return None

    @staticmethod
    def _extract_procedure_type(value: str) -> str:
        lowered = value.lower()
        for candidate in ("licitación pública", "licitación privada", "contratación abreviada", "adjudicación simple"):
            if candidate in lowered:
                return candidate.title()
        return value

    @staticmethod
    def _clean_text(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()
