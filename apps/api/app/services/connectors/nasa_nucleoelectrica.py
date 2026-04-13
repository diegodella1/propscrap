from __future__ import annotations

from datetime import UTC, datetime
import re

from bs4 import BeautifulSoup
import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.http_safety import assert_public_https_url


class NasaNucleoelectricaConnector(BaseConnector):
    slug = "nasa-nucleoelectrica"
    name = "Nucleoeléctrica"
    base_url = "https://www.boletinoficial.gob.ar"
    section_url = "https://www.boletinoficial.gob.ar/seccion/tercera"
    org_markers = (
        "nucleoeléctrica argentina",
        "nucleoelectrica argentina",
        "na-sa",
    )

    def fetch(self) -> list[RawTenderRecord]:
        assert_public_https_url(self.section_url, label="nasa.section_url")
        settings = get_settings()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.get(self.section_url)
            response.raise_for_status()
            html = response.text
        return self._extract_records(html)

    def _extract_records(self, html: str) -> list[RawTenderRecord]:
        soup = BeautifulSoup(html, "lxml")
        publication_dt = self._parse_section_date(soup)
        items: list[RawTenderRecord] = []

        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            if not href.startswith("/detalleAviso/tercera/"):
                continue

            line = link.find("div", class_="linea-aviso")
            if not line:
                continue

            org_tag = line.find("p", class_="item")
            detail_tag = line.find("p", class_="item-detalle")
            if not org_tag or not detail_tag:
                continue

            organization = self._clean_text(org_tag.get_text(" ", strip=True))
            lowered_org = organization.lower()
            if not any(marker in lowered_org for marker in self.org_markers):
                continue

            procedure_text = self._clean_text(detail_tag.get_text(" ", strip=True))
            external_id = href.strip("/").split("/")[2]
            source_url = str(httpx.URL(self.base_url).join(href))

            items.append(
                RawTenderRecord(
                    external_id=external_id,
                    title=f"{organization} - {procedure_text}",
                    description_raw=procedure_text,
                    organization="Nucleoeléctrica Argentina S.A.",
                    jurisdiction="Nación",
                    procedure_type=self._extract_procedure_type(procedure_text),
                    publication_date=publication_dt.date() if publication_dt else None,
                    deadline_date=None,
                    opening_date=None,
                    estimated_amount=None,
                    currency="ARS",
                    source_url=source_url,
                    status_raw=procedure_text,
                )
            )

        if not items:
            raise ValueError("Nucleoeléctrica notices not found in current Boletín section")
        return items

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
        return datetime(
            int(match.group(3)),
            months[match.group(2).lower()],
            int(match.group(1)),
            tzinfo=UTC,
        )

    @staticmethod
    def _extract_procedure_type(value: str) -> str:
        lowered = value.lower()
        for candidate in (
            "licitación pública",
            "licitación privada",
            "concurso privado",
            "contratación directa",
            "desarrollo de proveedores",
        ):
            if candidate in lowered:
                return candidate.title()
        return "Aviso oficial"

    @staticmethod
    def _clean_text(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()
