from __future__ import annotations

from datetime import UTC, datetime
import re

from bs4 import BeautifulSoup
import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord


class BoletinOficialConnector(BaseConnector):
    slug = "boletin-oficial"
    name = "Boletín Oficial"
    base_url = "https://www.boletinoficial.gob.ar"
    section_url = "https://www.boletinoficial.gob.ar/seccion/tercera"

    def fetch(self) -> list[RawTenderRecord]:
        settings = get_settings()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.get(self.section_url)
            response.raise_for_status()
            html = response.text

        soup = BeautifulSoup(html, "lxml")
        section_date = self._parse_section_date(soup)
        items: list[RawTenderRecord] = []

        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            if not href.startswith("/detalleAviso/tercera/"):
                continue

            line = link.find("div", class_="linea-aviso")
            if not line:
                continue

            org = line.find("p", class_="item")
            detail = line.find("p", class_="item-detalle")
            if not org or not detail:
                continue

            procedure_text = self._clean_text(detail.get_text(" ", strip=True))
            organization = self._clean_text(org.get_text(" ", strip=True))
            title = f"{organization} - {procedure_text}"
            external_id = href.strip("/").split("/")[2]
            detail_url = httpx.URL(self.base_url).join(href)

            items.append(
                RawTenderRecord(
                    external_id=external_id,
                    title=title,
                    description_raw=None,
                    organization=organization,
                    jurisdiction="Nación",
                    procedure_type=self._extract_procedure_type(procedure_text),
                    publication_date=section_date.date() if section_date else None,
                    deadline_date=None,
                    opening_date=None,
                    estimated_amount=None,
                    currency="ARS",
                    source_url=str(detail_url),
                    status_raw=procedure_text,
                )
            )

        return items[:15]

    def fetch_detail_html(self, source_url: str) -> str | None:
        settings = get_settings()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.get(source_url)
            response.raise_for_status()
            return response.text

    @staticmethod
    def _parse_section_date(soup: BeautifulSoup) -> datetime | None:
        text = soup.get_text(" ", strip=True)
        match = re.search(r"Edición del\s+(\d{2}) de ([A-Za-zÁÉÍÓÚáéíóú]+) de (\d{4})", text)
        if not match:
            return None
        months = {
            "enero": 1,
            "febrero": 2,
            "marzo": 3,
            "abril": 4,
            "mayo": 5,
            "junio": 6,
            "julio": 7,
            "agosto": 8,
            "septiembre": 9,
            "octubre": 10,
            "noviembre": 11,
            "diciembre": 12,
        }
        day = int(match.group(1))
        month = months[match.group(2).lower()]
        year = int(match.group(3))
        return datetime(year, month, day, tzinfo=UTC)

    @staticmethod
    def _extract_procedure_type(value: str) -> str:
        lowered = value.lower()
        for candidate in ["licitación pública", "licitación privada", "concurso privado", "contratación directa"]:
            if candidate in lowered:
                return candidate.title()
        return "Aviso oficial"

    @staticmethod
    def _clean_text(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()

