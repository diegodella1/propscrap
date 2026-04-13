from __future__ import annotations

from datetime import UTC, datetime
import os
import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.http_safety import assert_public_https_url


class IntiPublicConnector(BaseConnector):
    slug = "inti"
    name = "INTI"
    base_url = "https://www.inti.gob.ar"
    sitemap_url = "https://www.inti.gob.ar/sitemap.xml"
    uploads_prefix = "https://www.inti.gob.ar/assets/uploads/contrataciones/"

    def fetch(self) -> list[RawTenderRecord]:
        assert_public_https_url(self.sitemap_url, label="inti.sitemap_url")
        settings = get_settings()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.get(self.sitemap_url)
            response.raise_for_status()
            xml = response.text
        return self._extract_records(xml)

    def _extract_records(self, xml: str) -> list[RawTenderRecord]:
        soup = BeautifulSoup(xml, "xml")
        items: list[RawTenderRecord] = []
        seen_ids: set[str] = set()

        for url_tag in soup.find_all("url"):
            loc_tag = url_tag.find("loc")
            lastmod_tag = url_tag.find("lastmod")
            if loc_tag is None:
                continue
            loc = self._clean_text(loc_tag.get_text(" ", strip=True))
            if not loc.startswith(self.uploads_prefix):
                continue

            publication_date = self._parse_lastmod(lastmod_tag.get_text(" ", strip=True) if lastmod_tag else "")
            external_id = self._extract_external_id(loc)
            title = self._build_title(loc)
            if not external_id or external_id in seen_ids:
                continue
            seen_ids.add(external_id)

            items.append(
                RawTenderRecord(
                    external_id=external_id,
                    title=title,
                    description_raw="Documento de contratación publicado en sitemap oficial de INTI",
                    organization="INTI",
                    jurisdiction="Nación",
                    procedure_type=self._extract_procedure_type(external_id, title),
                    publication_date=publication_date.date() if publication_date else None,
                    deadline_date=None,
                    opening_date=None,
                    estimated_amount=None,
                    currency="ARS",
                    source_url=loc,
                    status_raw="Documento publicado",
                )
            )

        if not items:
            raise ValueError("INTI procurement documents not found in sitemap")
        return items

    @staticmethod
    def _parse_lastmod(value: str) -> datetime | None:
        cleaned = value.strip()
        if not cleaned:
            return None
        try:
            parsed = datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)

    @staticmethod
    def _extract_external_id(url: str) -> str:
        filename = os.path.basename(urlparse(url).path)
        stem = re.sub(r"\.pdf$", "", filename, flags=re.IGNORECASE)
        return re.sub(r"[_\s]+", "-", stem).strip("-")

    @staticmethod
    def _build_title(url: str) -> str:
        filename = os.path.basename(urlparse(url).path)
        stem = re.sub(r"\.pdf$", "", filename, flags=re.IGNORECASE)
        pretty = re.sub(r"[_-]+", " ", stem).strip()
        return pretty or "Documento de contratación INTI"

    @staticmethod
    def _extract_procedure_type(external_id: str, title: str) -> str:
        haystack = f"{external_id} {title}".upper()
        if "LPNB" in haystack:
            return "Licitación Pública Nacional"
        if "LPNO" in haystack:
            return "Licitación Pública Nacional"
        if re.search(r"\bLP\d", haystack):
            return "Licitación Pública"
        if "CIRCULAR" in haystack:
            return "Circular"
        return "Documento de contratación"

    @staticmethod
    def _clean_text(value: str) -> str:
        return " ".join(value.split()).strip()
