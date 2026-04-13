from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
import html
import re

from bs4 import BeautifulSoup
import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.http_safety import assert_public_https_url

SPANISH_MONTHS = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "setiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}


class NeuquenConnector(BaseConnector):
    slug = "licitaciones-neuquen"
    name = "Provincia del Neuquén"
    base_url = "https://salud.neuquen.gob.ar"
    page_url = "https://salud.neuquen.gob.ar/category/licitaciones/"

    def fetch(self) -> list[RawTenderRecord]:
        assert_public_https_url(self.page_url, label="neuquen.page_url")
        settings = get_settings()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.get(self.page_url)
            response.raise_for_status()
            html_text = response.text
        return self._extract_rows(html_text)

    def _extract_rows(self, html_text: str) -> list[RawTenderRecord]:
        soup = BeautifulSoup(html_text, "lxml")
        items: list[RawTenderRecord] = []
        for article in soup.find_all("article", class_="post"):
            title_node = article.find("h2", class_="entry-title")
            anchor = title_node.find("a", href=True) if title_node else None
            excerpt_node = article.find("p")
            if anchor is None or excerpt_node is None:
                continue

            title = self._clean_text(anchor.get_text(" ", strip=True))
            excerpt = self._clean_text(html.unescape(excerpt_node.get_text(" ", strip=True)))
            if not title:
                continue
            opening_date = self._extract_opening_datetime(excerpt)

            items.append(
                RawTenderRecord(
                    external_id=self._extract_external_id(title, excerpt) or anchor["href"],
                    title=title,
                    description_raw=excerpt or None,
                    organization="Ministerio de Salud de la Provincia del Neuquén",
                    jurisdiction="Provincia del Neuquén",
                    procedure_type=self._extract_procedure_type(excerpt),
                    publication_date=opening_date.date() if opening_date else None,
                    deadline_date=opening_date,
                    opening_date=opening_date,
                    estimated_amount=self._extract_estimated_amount(excerpt),
                    currency="ARS",
                    source_url=anchor["href"],
                    status_raw="Publicada",
                )
            )

        if not items:
            raise ValueError("Neuquén licitaciones rows not found")
        return items

    @staticmethod
    def _extract_external_id(title: str, excerpt: str) -> str | None:
        for pattern in (
            r"(EX-\d{4}-[A-Z0-9#-]+)",
            r"(EX-\d{4}-\d{6,}-[A-Z0-9#-]+)",
            r"N[°º]?\s*([0-9]+)",
        ):
            for text in (excerpt, title):
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1)
        return None

    @staticmethod
    def _extract_procedure_type(text: str) -> str | None:
        match = re.search(r"(Licitación Pública(?:\s*\(.*?\))?)", text, re.IGNORECASE)
        if match:
            return NeuquenConnector._clean_text(match.group(1))
        return "Licitación Pública"

    @staticmethod
    def _extract_estimated_amount(text: str) -> Decimal | None:
        match = re.search(r"\$\s*([0-9\.\,\s]+)", text)
        if match is None:
            return None
        normalized = match.group(1).replace(".", "").replace(" ", "").replace(",", ".")
        try:
            return Decimal(normalized)
        except Exception:
            return None

    @staticmethod
    def _extract_opening_datetime(text: str) -> datetime | None:
        match = re.search(
            r"Fecha\s*[–-]\s*hora y lugar de apertura:\s*([0-9]{1,2})\s+de\s+([A-Za-záéíóúÁÉÍÓÚ]+)\s+de\s+([0-9]{4}).{0,40}?Hora:\s*([0-9]{1,2})[,:.]([0-9]{2})",
            text,
            re.IGNORECASE,
        )
        if match is None:
            return None
        month = SPANISH_MONTHS.get(match.group(2).strip().lower())
        if month is None:
            return None
        return datetime(
            year=int(match.group(3)),
            month=month,
            day=int(match.group(1)),
            hour=int(match.group(4)),
            minute=int(match.group(5)),
        )

    @staticmethod
    def _clean_text(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()
