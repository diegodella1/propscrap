from __future__ import annotations

from datetime import UTC, datetime
import re

from bs4 import BeautifulSoup
import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.http_safety import assert_public_https_url


class PbacConnector(BaseConnector):
    slug = "pbac"
    name = "Compras PBAC"
    base_url = "https://pbac.cgp.gba.gov.ar"
    home_url = "https://pbac.cgp.gba.gov.ar/Default.aspx"
    listing_url = "https://pbac.cgp.gba.gov.ar/ListarAperturaProxima.aspx"
    table_id = "ctl00_CPH1_CtrlTablasPortal_gridPliegoAperturaProxima"

    def fetch(self) -> list[RawTenderRecord]:
        assert_public_https_url(self.home_url, label="pbac.home_url")
        settings = get_settings()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.get(self.home_url)
            response.raise_for_status()
            html = response.text

        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table", id=self.table_id)
        if table is None:
            raise ValueError("PBAC opening-soon table not found")

        records: list[RawTenderRecord] = []
        for row in table.find_all("tr")[1:]:
            cells = row.find_all("td")
            if len(cells) < 6:
                continue

            external_id = self._clean_text(cells[0].get_text(" ", strip=True))
            title = self._clean_text(cells[1].get_text(" ", strip=True))
            procedure_type = self._clean_text(cells[2].get_text(" ", strip=True))
            opening_date = self._parse_datetime(cells[3].get_text(" ", strip=True))
            status_raw = self._clean_text(cells[4].get_text(" ", strip=True))
            organization = self._clean_text(cells[5].get_text(" ", strip=True))

            records.append(
                RawTenderRecord(
                    external_id=external_id,
                    title=title,
                    description_raw=f"{status_raw}. {organization}",
                    organization=organization,
                    jurisdiction="Provincia de Buenos Aires",
                    procedure_type=procedure_type,
                    publication_date=opening_date.date() if opening_date else None,
                    deadline_date=opening_date,
                    opening_date=opening_date,
                    estimated_amount=None,
                    currency="ARS",
                    source_url=self.listing_url,
                    status_raw=status_raw,
                )
            )

        return records[:15]

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            parsed = datetime.strptime(value.strip(), "%d/%m/%Y %H:%M Hrs.")
        except ValueError:
            return None
        return parsed.replace(tzinfo=UTC)

    @staticmethod
    def _clean_text(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()
