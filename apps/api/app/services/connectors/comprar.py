from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
import re

from bs4 import BeautifulSoup
import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.http_safety import assert_public_https_url


class ComprarConnector(BaseConnector):
    slug = "comprar"
    name = "COMPR.AR"
    base_url = "https://comprar.gob.ar"
    home_url = "https://comprar.gob.ar/"
    table_id = "ctl00_CPH1_CtrlConsultasFrecuentes_gvListadoPliegos"

    def fetch(self) -> list[RawTenderRecord]:
        assert_public_https_url(self.home_url, label="comprar.home_url")
        settings = get_settings()
        headers = {
            "User-Agent": settings.user_agent,
        }
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers=headers,
            follow_redirects=True,
        ) as client:
            response = client.get(self.home_url)
            response.raise_for_status()
            html = response.text

        return self._extract_rows(html)

    def _extract_rows(self, html: str) -> list[RawTenderRecord]:
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table", id=self.table_id)
        if table is None:
            raise ValueError("COMPR.AR public listing table not found")

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
            source_url = self._extract_source_url(process_link.get("onclick", "") if process_link else "")

            items.append(
                RawTenderRecord(
                    external_id=external_id or None,
                    title=title or "Sin titulo",
                    description_raw=None,
                    organization=organization or None,
                    jurisdiction="Nación",
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
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None

        try:
            parsed = datetime.strptime(value.strip(), "%d/%m/%Y %H:%M Hrs.")
        except ValueError:
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return None
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
        return parsed.replace(tzinfo=UTC)

    @staticmethod
    def _parse_decimal(value: str | None) -> Decimal | None:
        if not value:
            return None
        normalized = value.replace(".", "").replace(",", ".").strip()
        try:
            return Decimal(normalized)
        except (InvalidOperation, AttributeError):
            return None

    @staticmethod
    def _clean_text(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()

    def _extract_source_url(self, onclick: str) -> str:
        match = re.search(r"redireccionar\('([^']+)'\)", onclick)
        if not match:
            return self.base_url
        return str(httpx.URL(self.base_url).join(match.group(1)))
