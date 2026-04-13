from __future__ import annotations

from datetime import UTC, datetime
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.http_safety import assert_public_https_url


class MendozaConnector(BaseConnector):
    slug = "licitaciones-mendoza"
    name = "Provincia de Mendoza"
    base_url = "https://comprar.mendoza.gov.ar"
    home_url = "https://comprar.mendoza.gov.ar/"

    def fetch(self) -> list[RawTenderRecord]:
        assert_public_https_url(self.home_url, label="mendoza.home_url")
        settings = get_settings()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.get(self.home_url)
            response.raise_for_status()
            html = response.text
        return self._extract_rows(html)

    def _extract_rows(self, html: str) -> list[RawTenderRecord]:
        soup = BeautifulSoup(html, "lxml")
        table = self._find_procurement_table(soup)
        if table is None:
            raise ValueError("Mendoza public listing table not found")

        items: list[RawTenderRecord] = []
        for row in table.find_all("tr")[1:]:
            cells = row.find_all("td")
            if len(cells) < 5:
                continue

            process_link = cells[0].find("a")
            external_id = self._clean_text(cells[0].get_text(" ", strip=True))
            title = self._clean_text(cells[1].get_text(" ", strip=True))
            procedure_type = self._clean_text(cells[2].get_text(" ", strip=True))
            opening_date = self._parse_datetime(cells[3].get_text(" ", strip=True))
            organization = self._clean_text(cells[4].get_text(" ", strip=True))
            source_url = self._extract_source_url(
                process_link.get("onclick", "") if process_link and process_link.get("onclick") else process_link.get("href", "") if process_link else ""
            )

            if not external_id or not title:
                continue

            items.append(
                RawTenderRecord(
                    external_id=external_id,
                    title=title,
                    description_raw=None,
                    organization=organization or None,
                    jurisdiction="Provincia de Mendoza",
                    procedure_type=procedure_type or None,
                    publication_date=opening_date.date() if opening_date else None,
                    deadline_date=opening_date,
                    opening_date=opening_date,
                    estimated_amount=None,
                    currency="ARS",
                    source_url=source_url,
                    status_raw="Apertura próxima",
                )
            )

        return items

    @staticmethod
    def _find_procurement_table(soup: BeautifulSoup):
        for table in soup.find_all("table"):
            header = " ".join(th.get_text(" ", strip=True).lower() for th in table.find_all("th"))
            if "número de proceso" in header and "fecha de apertura" in header:
                return table
        return None

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        raw = value.strip()
        for fmt in ("%d/%m/%Y %H:%M Hrs.", "%d/%m/%Y %H:%M"):
            try:
                return datetime.strptime(raw, fmt).replace(tzinfo=UTC)
            except ValueError:
                continue
        return None

    @staticmethod
    def _clean_text(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()

    def _extract_source_url(self, href: str) -> str:
        if not href:
            return self.home_url
        match = re.search(r"redireccionar\('([^']+)'\)", href)
        if match:
            return urljoin(f"{self.base_url}/", match.group(1))
        if href.startswith("javascript:"):
            return self.home_url
        return str(httpx.URL(self.base_url).join(href))
