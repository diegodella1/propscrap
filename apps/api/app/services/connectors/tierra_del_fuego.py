from __future__ import annotations

from datetime import datetime
import re

from bs4 import BeautifulSoup
import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.http_safety import assert_public_https_url


class TierraDelFuegoConnector(BaseConnector):
    slug = "licitaciones-tierra-del-fuego"
    name = "Provincia de Tierra del Fuego"
    base_url = "https://compras.tierradelfuego.gob.ar"
    page_url = "https://compras.tierradelfuego.gob.ar/?cat=19"

    def fetch(self) -> list[RawTenderRecord]:
        assert_public_https_url(self.page_url, label="tierra_del_fuego.page_url")
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
        items: list[RawTenderRecord] = []
        for article in soup.find_all("article"):
            title_link = article.find("h3", class_="the-title")
            anchor = title_link.find("a", href=True) if title_link else None
            excerpt_node = article.find("div", class_="the-excerpt")
            time_node = article.find("time")
            if anchor is None or excerpt_node is None:
                continue

            title = self._clean_text(anchor.get_text(" ", strip=True))
            excerpt = self._clean_text(excerpt_node.get_text(" ", strip=True))
            lowered = f"{title} {excerpt}".lower()
            if any(token in lowered for token in ("adjudic", "pre adjudic", "circular modificatoria", "fracas")):
                continue

            external_id = self._extract_external_id(title, excerpt, anchor["href"])
            if not title or not external_id:
                continue

            publication_date = self._parse_date(time_node.get("datetime")) if time_node else None
            items.append(
                RawTenderRecord(
                    external_id=external_id,
                    title=title,
                    description_raw=excerpt or None,
                    organization="Provincia de Tierra del Fuego",
                    jurisdiction="Provincia de Tierra del Fuego",
                    procedure_type="Licitación Pública",
                    publication_date=publication_date,
                    deadline_date=None,
                    opening_date=None,
                    estimated_amount=None,
                    currency="ARS",
                    source_url=anchor["href"],
                    status_raw="Publicada",
                )
            )

        if not items:
            raise ValueError("Tierra del Fuego licitaciones rows not found")
        return items

    @staticmethod
    def _parse_date(value: str | None):
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None

    @staticmethod
    def _extract_external_id(title: str, excerpt: str, source_url: str) -> str | None:
        for text in (title, excerpt):
            match = re.search(r"N[°º]\s*([0-9]+(?:[-/][0-9]+)+)", text, re.IGNORECASE)
            if match:
                return match.group(1).replace("-", "/")
        match = re.search(r"[?&]p=(\d+)", source_url)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def _clean_text(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()
