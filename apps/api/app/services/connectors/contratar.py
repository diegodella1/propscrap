from __future__ import annotations

import csv
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from io import StringIO
import re

import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.http_safety import assert_public_https_url


class ContratarConnector(BaseConnector):
    slug = "contratar"
    name = "CONTRAT.AR"
    base_url = "https://contratar.gob.ar"
    search_url = "https://contratar.gob.ar/BuscarAvanzado.aspx"
    dataset_url = "https://infra.datos.gob.ar/catalog/jgm/dataset/30/distribution/30.1/download/onc-contratar-procedimientos.csv"
    max_items = 500

    def fetch(self) -> list[RawTenderRecord]:
        assert_public_https_url(self.dataset_url, label="contratar.dataset_url")
        settings = get_settings()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.get(self.dataset_url)
            response.raise_for_status()
        return self._parse_csv(response.text)

    def fetch_detail_html(self, source_url: str) -> str | None:
        if not source_url:
            return None
        settings = get_settings()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.get(source_url)
            response.raise_for_status()
            return response.text

    def _parse_csv(self, csv_text: str) -> list[RawTenderRecord]:
        reader = csv.DictReader(StringIO(csv_text))
        items: list[tuple[datetime | None, RawTenderRecord]] = []

        for row in reader:
            external_id = self._clean(row.get("procedimiento_numero"))
            title = self._clean(row.get("procedimiento_nombre")) or self._clean(row.get("procedimiento_objeto"))
            organization = self._clean(row.get("organismo_nombre"))
            procedure_type = self._clean(row.get("procedimiento_tipo"))
            status_raw = self._clean(row.get("procedimiento_estado"))
            publication_dt = self._parse_datetime(row.get("publicacion_contratar_fecha")) or self._parse_datetime(
                row.get("publicacion_bora_fecha")
            )
            deadline_dt = self._parse_datetime(row.get("consultas_fin_fecha"))
            amount = self._parse_decimal(row.get("presupuesto_oficial_monto"))
            source_url = self._build_source_url(external_id)
            description = self._build_description(row)

            if not external_id or not title:
                continue

            record = RawTenderRecord(
                external_id=external_id,
                title=title,
                description_raw=description,
                organization=organization,
                jurisdiction="Nación",
                procedure_type=procedure_type,
                publication_date=publication_dt.date() if publication_dt else None,
                deadline_date=deadline_dt,
                opening_date=None,
                estimated_amount=amount,
                currency="ARS",
                source_url=source_url,
                status_raw=status_raw,
            )
            items.append((publication_dt, record))

        items.sort(key=lambda item: item[0] or datetime(1970, 1, 1, tzinfo=UTC), reverse=True)
        return [record for _, record in items[: self.max_items]]

    def _build_source_url(self, external_id: str) -> str:
        safe_external_id = httpx.QueryParams({"numeroProceso": external_id})
        return f"{self.search_url}?{safe_external_id}"

    def _build_description(self, row: dict[str, str | None]) -> str | None:
        parts = [
            self._clean(row.get("procedimiento_objeto")),
            self._clean(row.get("uoc_descripcion")),
            self._clean(row.get("sistema_contratacion")),
            self._clean(row.get("expediente_procedimiento_numero")),
        ]
        text = " | ".join(part for part in parts if part)
        return text or None

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        raw = value.strip()
        if not raw:
            return None
        candidates = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]
        for fmt in candidates:
            try:
                return datetime.strptime(raw, fmt).replace(tzinfo=UTC)
            except ValueError:
                continue
        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return None
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)

    @staticmethod
    def _parse_decimal(value: str | None) -> Decimal | None:
        if not value:
            return None
        normalized = value.strip().replace(",", ".")
        if not normalized:
            return None
        try:
            return Decimal(normalized)
        except (InvalidOperation, ValueError):
            return None

    @staticmethod
    def _clean(value: str | None) -> str | None:
        if value is None:
            return None
        text = re.sub(r"\s+", " ", value).strip()
        return text or None
