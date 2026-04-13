from __future__ import annotations

from datetime import UTC, datetime
import re

from bs4 import BeautifulSoup
import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.http_safety import assert_public_https_url


class ArsatConnector(BaseConnector):
    slug = "arsat"
    name = "ARSAT"
    base_url = "https://www.arsat.com.ar"
    page_url = "https://www.arsat.com.ar/acerca-de-arsat/transparencia-activa/compras-y-contrataciones/"

    def fetch(self) -> list[RawTenderRecord]:
        assert_public_https_url(self.page_url, label="arsat.page_url")
        settings = get_settings()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.get(self.page_url)
            response.raise_for_status()
            html = response.text
        return self._extract_records(html)

    def _extract_records(self, html: str) -> list[RawTenderRecord]:
        soup = BeautifulSoup(html, "lxml")
        lines = [
            self._clean_text(line)
            for line in soup.get_text("\n", strip=True).splitlines()
            if self._clean_text(line)
        ]

        items: list[RawTenderRecord] = []
        seen_ids: set[str] = set()
        for block in self._iter_procurement_blocks(lines):
            title = block[0]
            deadline_info = self._find_schedule(block, kind="deadline")
            opening_info = self._find_schedule(block, kind="opening")
            if deadline_info is None or opening_info is None:
                continue

            external_id = self._extract_external_id(title, block)
            if external_id in seen_ids:
                continue
            seen_ids.add(external_id)
            deadline_date = self._parse_datetime(deadline_info[0], deadline_info[1])
            opening_date = self._parse_datetime(opening_info[0], opening_info[1])
            items.append(
                RawTenderRecord(
                    external_id=external_id,
                    title=title,
                    description_raw=title,
                    organization="ARSAT",
                    jurisdiction="Nación",
                    procedure_type=self._extract_procedure_type(title),
                    publication_date=opening_date.date() if opening_date else None,
                    deadline_date=deadline_date,
                    opening_date=opening_date,
                    estimated_amount=None,
                    currency="ARS",
                    source_url=self.page_url,
                    status_raw="Publicada",
                )
            )

        if not items:
            raise ValueError("ARSAT procurement blocks not found")
        return items

    @staticmethod
    def _iter_procurement_blocks(lines: list[str]) -> list[list[str]]:
        title_pattern = re.compile(r"^(Licitación|Invitación)\b", re.IGNORECASE)
        blocks: list[list[str]] = []
        current: list[str] = []
        for line in lines:
            if title_pattern.match(line):
                if current:
                    blocks.append(current)
                current = [line]
                continue
            if current:
                current.append(line)
        if current:
            blocks.append(current)
        return blocks

    @staticmethod
    def _find_schedule(block: list[str], *, kind: str) -> tuple[str, str] | None:
        if kind == "deadline":
            pattern = re.compile(
                r"Recepción de ofertas hasta el día\s*(\d{2}/\d{2}/\d{4})\s*a las\s*(\d{1,2}[.:]\d{2})",
                re.IGNORECASE,
            )
        else:
            pattern = re.compile(
                r"Acto de Apertura de ofertas el día\s*(\d{2}/\d{2}/\d{4})\s*a las\s*(\d{1,2}[.:]\d{2})",
                re.IGNORECASE,
            )
        for line in block[1:]:
            match = pattern.search(line)
            if match:
                return match.group(1), match.group(2)
        return None

    @staticmethod
    def _extract_external_id(title: str, block: list[str] | None = None) -> str:
        normalized = re.sub(r"\s+", " ", title).strip()
        match = re.search(r"(?:N[°º]\s*|[-–]\s*)(\d+/\d{4})\b", normalized, re.IGNORECASE)
        if match:
            return match.group(1)
        match = re.search(r"\b(?:LPN|LPri|LP|LicPri|LicPub)[\s-]*(\d+[-/]\d{4})\b", normalized, re.IGNORECASE)
        if match:
            return match.group(1).replace("-", "/")
        if block:
            for line in block[1:]:
                match = re.search(r"\b(?:LPN|LPri|LP|LicPri|LicPub)[\s-]*(\d+[-/]\d{4})\b", line, re.IGNORECASE)
                if match:
                    return match.group(1).replace("-", "/")
        return normalized[:80]

    @staticmethod
    def _extract_procedure_type(title: str) -> str:
        lowered = title.lower()
        for candidate in ("licitación pública", "licitación privada", "invitación a precalificar"):
            if candidate in lowered:
                return candidate.title()
        return "Proceso publicado"

    @staticmethod
    def _parse_datetime(date_value: str, time_value: str) -> datetime | None:
        raw = f"{date_value.strip()} {time_value.strip().replace('.', ':')}"
        for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y %I:%M"):
            try:
                return datetime.strptime(raw, fmt).replace(tzinfo=UTC)
            except ValueError:
                continue
        return None

    @staticmethod
    def _clean_text(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()
