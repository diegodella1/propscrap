from __future__ import annotations

from bs4 import BeautifulSoup
import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.http_safety import assert_public_https_url


class EntreRiosConnector(BaseConnector):
    slug = "licitaciones-entre-rios"
    name = "Provincia de Entre Ríos"
    base_url = "https://www.entrerios.gov.ar"
    page_url = "https://www.entrerios.gov.ar/contrataciones/licitaciones.php"
    default_search = {
        "estado": "2",
        "anio": "2025",
        "buscar": "Buscar",
    }

    def fetch(self) -> list[RawTenderRecord]:
        assert_public_https_url(self.page_url, label="entre_rios.page_url")
        settings = get_settings()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.post(self.page_url, data=self.default_search)
            response.raise_for_status()
            html = response.text
        return self._extract_rows(html)

    def _extract_rows(self, html: str) -> list[RawTenderRecord]:
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table", id="tabla-resultados")
        if table is None:
            raise ValueError("Entre Rios results table not found")

        items: list[RawTenderRecord] = []
        for row in table.find_all("tr")[1:]:
            cells = row.find_all("td")
            if len(cells) < 4:
                continue

            procedure = self._clean_text(cells[0].get_text(" ", strip=True))
            title = self._clean_text(cells[1].get_text(" ", strip=True))
            destination = self._clean_text(cells[2].get_text(" ", strip=True))
            organization = self._clean_text(cells[3].get_text(" ", strip=True))
            external_id = self._extract_external_id(procedure)

            if not procedure or not title:
                continue

            description = destination or None
            if description and organization:
                description = f"Destino: {destination} | Organismo: {organization}"

            items.append(
                RawTenderRecord(
                    external_id=external_id,
                    title=title,
                    description_raw=description,
                    organization=organization or None,
                    jurisdiction="Provincia de Entre Ríos",
                    procedure_type=self._extract_procedure_type(procedure),
                    publication_date=None,
                    deadline_date=None,
                    opening_date=None,
                    estimated_amount=None,
                    currency="ARS",
                    source_url=self.page_url,
                    status_raw="En proceso de evaluación",
                )
            )

        if not items:
            raise ValueError("Entre Rios procurement rows not found")
        return items

    @staticmethod
    def _clean_text(value: str) -> str:
        return " ".join(value.split())

    @staticmethod
    def _extract_external_id(procedure: str) -> str | None:
        parts = procedure.split()
        return parts[-1] if parts else None

    @staticmethod
    def _extract_procedure_type(procedure: str) -> str | None:
        if "/" in procedure:
            return procedure.rsplit(" ", 1)[0].strip() or None
        return procedure or None
