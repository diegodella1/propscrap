from __future__ import annotations

from datetime import UTC, datetime
import re

from bs4 import BeautifulSoup
import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.http_safety import assert_public_https_url


class PamiConnector(BaseConnector):
    slug = "pami"
    name = "PAMI"
    base_url = "https://prestadores.pami.org.ar"
    page_url = "https://transparenciaactiva.pami.org.ar/compras-y-contrataciones/"
    calendar_url = "https://prestadores.pami.org.ar/result.php?c=7-1-1-3&par=1"

    def fetch(self) -> list[RawTenderRecord]:
        assert_public_https_url(self.calendar_url, label="pami.calendar_url")
        settings = get_settings()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.get(self.calendar_url)
            response.raise_for_status()
            html = response.text
        return self._extract_records(html)

    def _extract_records(self, html: str) -> list[RawTenderRecord]:
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text("\n", strip=True)
        normalized = re.sub(r"\n{2,}", "\n", text)
        marker = "Calendario de Aperturas"
        if marker in normalized:
            normalized = normalized.split(marker, 1)[1]

        pattern = re.compile(
            r"(?P<opening>\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2})\s+"
            r"(?P<procedure>Licitación\s+[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+|Compulsa\s+[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+|Concurso\s+[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+|Contratación\s+[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)\s+"
            r"(?P<expediente>\d+/\d+)\s+"
            r"(?P<title>.+?)(?=\s+\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}\s+(?:Licitación|Compulsa|Concurso|Contratación)\s+|(?:\s+Volver)?$)",
            re.IGNORECASE | re.DOTALL,
        )

        items: list[RawTenderRecord] = []
        seen_ids: set[str] = set()
        for match in pattern.finditer(normalized):
            opening_date = self._parse_datetime(match.group("opening"))
            procedure = self._clean_text(match.group("procedure"))
            external_id = self._clean_text(match.group("expediente"))
            title = self._clean_text(match.group("title").replace("remove_red_eye", ""))
            if not external_id or not title or external_id in seen_ids:
                continue
            seen_ids.add(external_id)
            items.append(
                RawTenderRecord(
                    external_id=external_id,
                    title=title,
                    description_raw=procedure,
                    organization="PAMI",
                    jurisdiction="Nación",
                    procedure_type=procedure,
                    publication_date=opening_date.date() if opening_date else None,
                    deadline_date=opening_date,
                    opening_date=opening_date,
                    estimated_amount=None,
                    currency="ARS",
                    source_url=self.calendar_url,
                    status_raw="Apertura próxima",
                )
            )

        if not items:
            raise ValueError("PAMI calendar records not found")

        return items

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.strptime(value.strip(), "%d/%m/%Y %H:%M").replace(tzinfo=UTC)
        except ValueError:
            return None

    @staticmethod
    def _clean_text(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()
