from __future__ import annotations

from datetime import UTC, datetime
import re

from bs4 import BeautifulSoup
import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.http_safety import assert_public_https_url


class ArsatConnector(BaseConnector):
    slug = "arsat"
    name = "ARSAT"
    base_url = "https://www.arsat.com.ar"
    page_url = "https://www.arsat.com.ar/acerca-de-arsat/transparencia-activa/compras-y-contrataciones/"

    def fetch(self) -> list[RawTenderRecord]:
        assert_public_https_url(self.page_url, label="arsat.page_url")
        settings = get_settings()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.get(self.page_url)
            response.raise_for_status()
            html = response.text
        return self._extract_records(html)

    def _extract_records(self, html: str) -> list[RawTenderRecord]:
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text("\n", strip=True)
        normalized = re.sub(r"\n{2,}", "\n", text)
        pattern = re.compile(
            r"(?P<title>(?:Licitación|Invitación)[^\n]+)\n"
            r".*?Recepción de ofertas hasta el día\s*(?P<deadline>\d{2}/\d{2}/\d{4})\s*a las\s*(?P<deadline_time>\d{1,2}[.:]\d{2})\s*horas?"
            r".*?Acto de Apertura de ofertas el día\s*(?P<opening>\d{2}/\d{2}/\d{4})\s*a las\s*(?P<opening_time>\d{1,2}[.:]\d{2})\s*horas?",
            re.IGNORECASE | re.DOTALL,
        )

        items: list[RawTenderRecord] = []
        seen_ids: set[str] = set()
        for match in pattern.finditer(normalized):
            title = self._clean_text(match.group("title"))
            external_id = self._extract_external_id(title)
            if external_id in seen_ids:
                continue
            seen_ids.add(external_id)
            deadline_date = self._parse_datetime(match.group("deadline"), match.group("deadline_time"))
            opening_date = self._parse_datetime(match.group("opening"), match.group("opening_time"))
            items.append(
                RawTenderRecord(
                    external_id=external_id,
                    title=title,
                    description_raw=title,
                    organization="ARSAT",
                    jurisdiction="Nación",
                    procedure_type=self._extract_procedure_type(title),
                    publication_date=opening_date.date() if opening_date else None,
                    deadline_date=deadline_date,
                    opening_date=opening_date,
                    estimated_amount=None,
                    currency="ARS",
                    source_url=self.page_url,
                    status_raw="Publicada",
                )
            )

        if not items:
            raise ValueError("ARSAT procurement blocks not found")
        return items

    @staticmethod
    def _extract_external_id(title: str) -> str:
        match = re.search(r"N[°º]\s*([A-Z]*\s*\d+/\d+)", title, re.IGNORECASE)
        if match:
            return re.sub(r"\s+", "", match.group(1).upper())
        return title[:80]

    @staticmethod
    def _extract_procedure_type(title: str) -> str:
        lowered = title.lower()
        for candidate in ("licitación pública", "licitación privada", "invitación a precalificar"):
            if candidate in lowered:
                return candidate.title()
        return "Proceso publicado"

    @staticmethod
    def _parse_datetime(date_value: str, time_value: str) -> datetime | None:
        raw = f"{date_value.strip()} {time_value.strip().replace('.', ':')}"
        for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y %I:%M"):
            try:
                return datetime.strptime(raw, fmt).replace(tzinfo=UTC)
            except ValueError:
                continue
        return None

    @staticmethod
    def _clean_text(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()
