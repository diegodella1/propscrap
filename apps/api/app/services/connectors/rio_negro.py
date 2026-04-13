from __future__ import annotations

from datetime import UTC, datetime
import re

from bs4 import BeautifulSoup
import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.http_safety import assert_public_https_url


class RioNegroConnector(BaseConnector):
    slug = "licitaciones-rio-negro"
    name = "Provincia de Río Negro"
    base_url = "https://comprar.rionegro.gov.ar"
    page_url = "https://comprar.rionegro.gov.ar/Compras.aspx?qs=iouVZE0yWCs="

    def fetch(self) -> list[RawTenderRecord]:
        assert_public_https_url(self.page_url, label="rio_negro.page_url")
        settings = get_settings()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.get(self.page_url)
            response.raise_for_status()
            html = response.text
        return self._extract_rows(html)

    def _extract_rows(self, html: str) -> list[RawTenderRecord]:
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table", id="ctl00_CPH1_GridListaPliegos")
        if table is None:
            raise ValueError("Río Negro procurement table not found")

        items: list[RawTenderRecord] = []
        for row in table.find_all("tr")[1:]:
            cells = row.find_all("td")
            if len(cells) < 7:
                continue

            external_id = self._clean_text(cells[0].get_text(" ", strip=True))
            title = self._clean_text(cells[1].get_text(" ", strip=True))
            procedure_type = self._clean_text(cells[2].get_text(" ", strip=True))
            opening_date = self._parse_datetime(cells[3].get_text(" ", strip=True))
            status_raw = self._clean_text(cells[4].get_text(" ", strip=True))
            organization = self._clean_text(cells[5].get_text(" ", strip=True))
            saf = self._clean_text(cells[6].get_text(" ", strip=True))

            if not external_id or not title:
                continue

            items.append(
                RawTenderRecord(
                    external_id=external_id,
                    title=title,
                    description_raw=saf or None,
                    organization=organization or None,
                    jurisdiction="Provincia de Río Negro",
                    procedure_type=procedure_type or None,
                    publication_date=opening_date.date() if opening_date else None,
                    deadline_date=opening_date,
                    opening_date=opening_date,
                    estimated_amount=None,
                    currency="ARS",
                    source_url=self.page_url,
                    status_raw=status_raw or None,
                )
            )

        if not items:
            raise ValueError("Río Negro procurement rows not found")
        return items

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.strptime(value.strip(), "%d/%m/%Y %H:%M Hrs.").replace(tzinfo=UTC)
        except ValueError:
            return None

    @staticmethod
    def _clean_text(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()
