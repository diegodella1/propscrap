from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
import re

import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.http_safety import assert_public_https_url

ARG_TZ = timezone(timedelta(hours=-3))


class SanJuanConnector(BaseConnector):
    slug = "licitaciones-san-juan"
    name = "Provincia de San Juan"
    base_url = "https://licitaciones.sanjuan.gob.ar"
    page_url = "https://licitaciones.sanjuan.gob.ar/"

    def fetch(self) -> list[RawTenderRecord]:
        assert_public_https_url(self.page_url, label="san_juan.page_url")
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
        match = re.search(r"var obj=(\{.*?\});", html, re.DOTALL)
        if match is None:
            raise ValueError("San Juan licitaciones JSON block not found")

        payload = json.loads(match.group(1))
        records = payload.get("licitaciones", {}).get("res", [])
        items: list[RawTenderRecord] = []
        for row in records:
            status_raw = self._clean_text(str(row.get("ESTADOS") or ""))
            if not self._is_active_status(status_raw):
                continue

            external_id = self._clean_text(str(row.get("N_PUB") or row.get("EXPEDIENTE") or row.get("ID_PUBLICACION") or ""))
            title = self._clean_text(str(row.get("OBJETO") or ""))
            if not external_id or not title:
                continue

            publication_date = self._parse_dotnet_datetime(row.get("F_PUBLICACION"))
            opening_date = self._parse_dotnet_datetime_with_time(row.get("F_APERTURA"), row.get("H_APERTURA"))
            deadline_date = self._parse_dotnet_datetime_with_time(row.get("FPRESENTACION"), row.get("H_PRESENTACION"))
            estimated_amount = self._parse_decimal(row.get("PRESUPUESTO"))
            detail_id = row.get("ID_PUBLICACION")

            details = [
                self._clean_text(str(row.get("EXPEDIENTE") or "")),
                self._clean_text(str(row.get("INFORMACION") or "")),
                self._clean_text(str(row.get("DOMI_APERTURA") or "")),
                self._clean_text(str(row.get("MAIL") or "")),
            ]
            description = " | ".join(value for value in details if value)

            items.append(
                RawTenderRecord(
                    external_id=external_id,
                    title=title,
                    description_raw=description or None,
                    organization=self._clean_text(str(row.get("INSTITUCION") or "")) or None,
                    jurisdiction="Provincia de San Juan",
                    procedure_type=self._clean_text(str(row.get("TIPO") or "")) or None,
                    publication_date=publication_date.date() if publication_date else None,
                    deadline_date=deadline_date,
                    opening_date=opening_date,
                    estimated_amount=estimated_amount,
                    currency="ARS",
                    source_url=f"{self.base_url}/index.php/detalle?id={detail_id}" if detail_id else self.page_url,
                    status_raw=status_raw or None,
                )
            )

        if not items:
            raise ValueError("San Juan licitaciones records not found")
        return items

    @staticmethod
    def _parse_dotnet_datetime(value: object) -> datetime | None:
        if not isinstance(value, str):
            return None
        match = re.search(r"/Date\((\d+)\)/", value)
        if match is None:
            return None
        return datetime.fromtimestamp(int(match.group(1)) / 1000, tz=ARG_TZ)

    def _parse_dotnet_datetime_with_time(self, date_value: object, time_value: object) -> datetime | None:
        base_date = self._parse_dotnet_datetime(date_value)
        if base_date is None:
            return None
        hours, minutes = self._parse_time(time_value)
        if hours is None or minutes is None:
            return base_date
        return base_date.replace(hour=hours, minute=minutes, second=0, microsecond=0)

    @staticmethod
    def _parse_time(value: object) -> tuple[int | None, int | None]:
        if not isinstance(value, str):
            return (None, None)
        raw = re.sub(r"\s+", " ", value).strip().upper()
        match = re.search(r"(\d{1,2})(?::|\.|,)?(\d{2})?\s*(AM|PM)?", raw)
        if match is None:
            return (None, None)
        hours = int(match.group(1))
        minutes = int(match.group(2) or "00")
        suffix = match.group(3)
        if suffix == "PM" and hours != 12:
            hours += 12
        if suffix == "AM" and hours == 12:
            hours = 0
        return (hours, minutes)

    @staticmethod
    def _parse_decimal(value: object) -> Decimal | None:
        if value in (None, ""):
            return None
        try:
            return Decimal(str(value))
        except Exception:
            return None

    @staticmethod
    def _is_active_status(value: str) -> bool:
        lowered = value.lower()
        return "apertura" in lowered or "prorrog" in lowered or "public" in lowered

    @staticmethod
    def _clean_text(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()
