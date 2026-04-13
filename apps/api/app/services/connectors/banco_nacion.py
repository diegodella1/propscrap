from __future__ import annotations

from datetime import UTC, datetime
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.http_safety import assert_public_https_url


class BancoNacionConnector(BaseConnector):
    slug = "banco-nacion"
    name = "Banco Nación"
    base_url = "https://www.bna.com.ar"
    listing_url = "https://www.bna.com.ar/Institucional/ComprasYContrataciones"
    results_url = "https://www.bna.com.ar/Institucional/ComprasYContratacionesResultados"

    def fetch(self) -> list[RawTenderRecord]:
        assert_public_https_url(self.results_url, label="banco_nacion.results_url")
        settings = get_settings()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.post(
                self.results_url,
                data={"filtro1": "2", "rubro": "0", "accion": "1"},
            )
            response.raise_for_status()
            html = response.text
        return self._extract_rows(html)

    def _extract_rows(self, html: str) -> list[RawTenderRecord]:
        soup = BeautifulSoup(html, "lxml")
        tables = soup.select("table.cotizador")
        if not tables:
            raise ValueError("Banco Nación procurement tables not found")

        today = datetime.now(tz=UTC).date()
        items: list[RawTenderRecord] = []
        seen_ids: set[str] = set()

        for table in tables:
            heading = table.find("th")
            category = self._clean_text(heading.get_text(" ", strip=True)) if heading else ""

            for row in table.select("tbody tr"):
                cells = row.find_all("td")
                if len(cells) < 8:
                    continue

                title = self._clean_text(cells[1].get_text(" ", strip=True))
                external_id = self._clean_text(cells[2].get_text(" ", strip=True))
                link = cells[3].find("a")
                source_url = self._extract_source_url(link.get("href", "") if link else "")
                opening_date = self._parse_datetime(
                    date_value=cells[5].get_text(" ", strip=True),
                    time_value=cells[6].get_text(" ", strip=True),
                )
                estimated_amount = self._parse_decimal(cells[7].get_text(" ", strip=True))

                if (
                    not title
                    or not external_id
                    or opening_date is None
                    or opening_date.date() < today
                    or external_id in seen_ids
                ):
                    continue
                seen_ids.add(external_id)

                called_text = self._clean_text(cells[2].get_text(" ", strip=True))
                procedure_type = self._extract_procedure_type(called_text)
                detail_parts = [part for part in (category, called_text) if part]

                items.append(
                    RawTenderRecord(
                        external_id=external_id,
                        title=title,
                        description_raw=" | ".join(detail_parts) or None,
                        organization="Banco Nación",
                        jurisdiction="Nación",
                        procedure_type=procedure_type,
                        publication_date=opening_date.date(),
                        deadline_date=opening_date,
                        opening_date=opening_date,
                        estimated_amount=estimated_amount,
                        currency="ARS",
                        source_url=source_url,
                        status_raw="Apertura próxima",
                    )
                )

        if not items:
            raise ValueError("Banco Nación upcoming procurement rows not found")

        return items

    def _extract_source_url(self, href: str) -> str:
        cleaned = self._clean_text(href)
        if not cleaned:
            return self.listing_url
        return urljoin(f"{self.base_url}/", cleaned)

    @staticmethod
    def _extract_procedure_type(value: str) -> str:
        lowered = value.lower()
        for candidate in ("licitación pública", "licitacion publica", "concurso público", "concurso publico"):
            if candidate in lowered:
                return candidate.replace("publica", "pública").replace("publico", "público").title()
        if re.search(r"\b(?:lpu|inm)\b", lowered):
            return "Licitación Pública"
        if re.search(r"\bcds\b", lowered):
            return "Contratación de Servicios"
        if re.search(r"\bcdb\b", lowered):
            return "Compra de Bienes"
        return "Proceso publicado"

    @staticmethod
    def _parse_datetime(*, date_value: str, time_value: str) -> datetime | None:
        date_clean = date_value.strip()
        time_clean = time_value.strip()
        if not date_clean or not time_clean:
            return None
        parts = [segment.strip() for segment in time_clean.split(":")]
        if len(parts) >= 2:
            normalized_time = f"{parts[0].zfill(2)}:{parts[1].zfill(2)}"
        else:
            normalized_time = time_clean
        raw = f"{date_clean} {normalized_time}"
        for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%y %H:%M", "%m/%d/%Y %H:%M"):
            try:
                return datetime.strptime(raw, fmt).replace(tzinfo=UTC)
            except ValueError:
                continue
        return None

    @staticmethod
    def _parse_decimal(value: str):
        cleaned = value.replace(".", "").replace(",", ".").strip()
        if not cleaned:
            return None
        try:
            from decimal import Decimal

            return Decimal(cleaned)
        except Exception:
            return None

    @staticmethod
    def _clean_text(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()
