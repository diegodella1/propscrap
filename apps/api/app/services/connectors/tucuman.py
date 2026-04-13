from __future__ import annotations

from datetime import UTC, datetime
import re

from bs4 import BeautifulSoup
import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.http_safety import assert_public_https_url


class TucumanConnector(BaseConnector):
    slug = "licitaciones-tucuman"
    name = "Provincia de Tucumán"
    base_url = "https://compras.tucuman.gob.ar"
    page_url = "https://compras.tucuman.gob.ar/ver_llamados_compras_avanzado.php?estado_compra=1"

    def fetch(self) -> list[RawTenderRecord]:
        assert_public_https_url(self.page_url, label="tucuman.page_url")
        settings = get_settings()
        items: list[RawTenderRecord] = []
        seen_ids: set[str] = set()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            first_page = client.get(self.page_url)
            first_page.raise_for_status()
            pages = self._extract_total_pages(first_page.text)
            for page_number in range(1, pages + 1):
                if page_number == 1:
                    html = first_page.text
                else:
                    response = client.get(
                        self.page_url,
                        params={"estado_compra": 1, "pagina_actual": page_number, "n": 1},
                    )
                    response.raise_for_status()
                    html = response.text

                for item in self._extract_rows(html):
                    if item.external_id and item.external_id in seen_ids:
                        continue
                    if item.external_id:
                        seen_ids.add(item.external_id)
                    items.append(item)

        if not items:
            raise ValueError("Tucumán procurement rows not found")
        return items

    def _extract_rows(self, html: str) -> list[RawTenderRecord]:
        soup = BeautifulSoup(html, "lxml")
        modals = soup.select("div.modal.fade[id^='myModal']")
        if not modals:
            raise ValueError("Tucumán procurement modals not found")

        items: list[RawTenderRecord] = []
        for modal in modals:
            content = modal.find("div", class_="modal-content")
            if content is None:
                continue

            organization = self._extract_organization(content)
            heading = self._extract_heading(content)
            procedure_type, external_id = self._parse_heading(heading)
            title = self._extract_title(content)
            expediente = self._extract_labeled_value(content, "Número de expediente:")
            opening_date = self._parse_datetime(self._extract_labeled_value(content, "Fecha y hora"))
            location = self._extract_labeled_value(content, "Lugar:")
            source_url = self._extract_source_url(content)

            if not external_id or not title:
                continue

            description_parts = [expediente, location]
            items.append(
                RawTenderRecord(
                    external_id=external_id,
                    title=title,
                    description_raw=" | ".join(part for part in description_parts if part) or None,
                    organization=organization or None,
                    jurisdiction="Provincia de Tucumán",
                    procedure_type=procedure_type or None,
                    publication_date=opening_date.date() if opening_date else None,
                    deadline_date=opening_date,
                    opening_date=opening_date,
                    estimated_amount=None,
                    currency="ARS",
                    source_url=source_url,
                    status_raw="Convocatoria",
                )
            )

        return items

    def _extract_total_pages(self, html: str) -> int:
        match = re.search(r"P[aá]gina\s+\d+\s+de\s+(\d+)", html, re.IGNORECASE)
        if match is None:
            return 1
        return max(1, int(match.group(1)))

    def _extract_organization(self, content: BeautifulSoup) -> str:
        tag = content.find("p", attrs={"align": "center"})
        if tag is None:
            return ""
        bold = tag.find("b")
        return self._clean_text(bold.get_text(" ", strip=True) if bold else tag.get_text(" ", strip=True))

    def _extract_heading(self, content: BeautifulSoup) -> str:
        for paragraph in content.find_all("p"):
            text = self._clean_text(paragraph.get_text(" ", strip=True))
            if "Nº" in text or "N°" in text or "N°" in paragraph.decode_contents():
                return text
        return ""

    def _parse_heading(self, heading: str) -> tuple[str, str]:
        clean_heading = self._clean_text(heading)
        match = re.search(r"(?P<procedure>.+?)\s+N[º°]\s*(?P<external_id>[\d./-]+)", clean_heading, re.IGNORECASE)
        if match is None:
            return "", ""
        return self._clean_text(match.group("procedure")), self._clean_text(match.group("external_id"))

    def _extract_title(self, content: BeautifulSoup) -> str:
        for cell in content.find_all("td"):
            text = self._clean_text(cell.get_text(" ", strip=True))
            if text and "Rubro:" in text:
                return text.split("-Rubro:", 1)[0].strip()
        paragraph = content.find("p", attrs={"align": "justify"})
        if paragraph is not None:
            return self._clean_text(paragraph.get_text(" ", strip=True))
        return ""

    def _extract_labeled_value(self, content: BeautifulSoup, label: str) -> str:
        for row in content.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 2:
                continue
            left = self._clean_text(cells[0].get_text(" ", strip=True)).rstrip(":")
            if left.lower() == label.rstrip(":").lower():
                return self._clean_text(cells[1].get_text(" ", strip=True))
        return ""

    def _extract_source_url(self, content: BeautifulSoup) -> str:
        for link in content.find_all("a"):
            onclick = link.get("onClick") or link.get("onclick") or ""
            match = re.search(r"window\.open\('([^']+detalle_llamado\.php\?id_compra=\d+)'", onclick)
            if match is not None:
                return match.group(1)
        return self.page_url

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        for fmt in ("%d/%m/%Y, %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y, %H:%M"):
            try:
                return datetime.strptime(value.strip(), fmt).replace(tzinfo=UTC)
            except ValueError:
                continue
        return None

    @staticmethod
    def _clean_text(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()
