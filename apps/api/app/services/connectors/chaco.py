from __future__ import annotations

from datetime import UTC, datetime
import re

from bs4 import BeautifulSoup
import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.http_safety import assert_public_https_url


class ChacoConnector(BaseConnector):
    slug = "licitaciones-chaco"
    name = "Provincia del Chaco"
    base_url = "https://compras.chaco.gob.ar"
    list_url = "https://compras.chaco.gob.ar/organismos/28?page=1"
    organization_name = "Provincia del Chaco"

    def fetch(self) -> list[RawTenderRecord]:
        assert_public_https_url(self.list_url, label="chaco.list_url")
        settings = get_settings()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.get(self.list_url)
            response.raise_for_status()
            html = response.text
        return self._extract_rows(html)

    def _extract_rows(self, html: str) -> list[RawTenderRecord]:
        soup = BeautifulSoup(html, "lxml")
        table = self._find_procurement_table(soup)
        if table is None:
            raise ValueError("Chaco procurement table not found")

        items: list[RawTenderRecord] = []
        for row in table.find_all("tr")[1:]:
            cells = row.find_all("td")
            if len(cells) < 4:
                continue

            link = cells[0].find("a") or row.find("a", href=True)
            external_id = self._clean_text(cells[0].get_text(" ", strip=True))
            title = self._clean_text(cells[1].get_text(" ", strip=True))
            procedure_type = self._clean_text(cells[2].get_text(" ", strip=True))
            opening_date = self._parse_datetime(cells[3].get_text(" ", strip=True))
            source_url = self._extract_source_url(link.get("href", "") if link else "")

            if not external_id or not title:
                continue

            items.append(
                RawTenderRecord(
                    external_id=external_id,
                    title=title,
                    description_raw=title,
                    organization=self.organization_name,
                    jurisdiction="Provincia del Chaco",
                    procedure_type=procedure_type or None,
                    publication_date=opening_date.date() if opening_date else None,
                    deadline_date=opening_date,
                    opening_date=opening_date,
                    estimated_amount=None,
                    currency="ARS",
                    source_url=source_url,
                    status_raw=procedure_type,
                )
            )

        return items

    @staticmethod
    def _find_procurement_table(soup: BeautifulSoup):
        for table in soup.find_all("table"):
            header = " ".join(th.get_text(" ", strip=True).lower() for th in table.find_all("th"))
            if "número de licitación" in header and "fecha de apertura" in header:
                return table
        return None

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.strptime(value.strip(), "%d/%m/%Y").replace(tzinfo=UTC)
        except ValueError:
            return None

    @staticmethod
    def _clean_text(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()

    def _extract_source_url(self, href: str) -> str:
        if not href:
            return self.list_url
        return str(httpx.URL(self.base_url).join(href))
