from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.http_safety import assert_public_https_url


class CordobaConnector(BaseConnector):
    slug = "licitaciones-cordoba"
    name = "Provincia de Córdoba"
    base_url = "https://compras.cordoba.gob.ar"
    list_url = "https://compras.cordoba.gob.ar/apifg/compra/compra"
    page_size = 100

    def fetch(self) -> list[RawTenderRecord]:
        assert_public_https_url(self.list_url, label="cordoba.list_url")
        settings = get_settings()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent, "Accept": "application/json"},
            follow_redirects=True,
        ) as client:
            response = client.get(
                self.list_url,
                params={
                    "pagina": 1,
                    "cantidad_filas": self.page_size,
                    "tipo_compra": "TODOS",
                    "activas": "true",
                    "busqueda": "",
                },
            )
            response.raise_for_status()
            payload = response.json()
        return self._extract_records(payload)

    def _extract_records(self, payload: dict[str, Any]) -> list[RawTenderRecord]:
        rows = payload.get("compras")
        if not isinstance(rows, list):
            raise ValueError("Córdoba procurement payload has invalid data shape")

        items: list[RawTenderRecord] = []
        seen_ids: set[str] = set()
        for row in rows:
            if not isinstance(row, dict):
                continue

            external_id = self._clean_text(str(row.get("titulo") or ""))
            title = self._clean_text(str(row.get("objeto") or ""))
            if not external_id or not title or external_id in seen_ids:
                continue
            seen_ids.add(external_id)

            publication_date = self._parse_datetime(row.get("fecha_publicacion"))
            opening_date = self._parse_call_datetime(row.get("ultimo_llamado"))
            organization = self._nested_name(row.get("entidad"))
            secretaria = self._nested_name(row.get("subentidad"))
            expediente = self._clean_text(str(row.get("expediente") or ""))
            procedure_type = self._nested_name(row.get("nombre_compra")) or self._nested_name(row.get("tipo"))
            status_raw = self._nested_name(row.get("estado"))
            detail_url = self._build_detail_url(row.get("id"))

            description_parts = [expediente, secretaria]
            items.append(
                RawTenderRecord(
                    external_id=external_id,
                    title=title,
                    description_raw=" | ".join(part for part in description_parts if part) or None,
                    organization=organization or None,
                    jurisdiction="Provincia de Córdoba",
                    procedure_type=procedure_type or None,
                    publication_date=publication_date.date() if publication_date else None,
                    deadline_date=opening_date,
                    opening_date=opening_date,
                    estimated_amount=None,
                    currency="ARS",
                    source_url=detail_url,
                    status_raw=status_raw or None,
                )
            )

        if not items:
            raise ValueError("Córdoba procurement records not found")
        return items

    @staticmethod
    def _parse_datetime(value: Any) -> datetime | None:
        if not value:
            return None
        raw = str(value).strip()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(raw, fmt).replace(tzinfo=UTC)
            except ValueError:
                continue
        return None

    def _parse_call_datetime(self, data: Any) -> datetime | None:
        if not isinstance(data, dict):
            return None
        date_value = self._clean_text(str(data.get("fecha_desde") or ""))
        time_value = self._clean_text(str(data.get("hora_desde") or ""))
        raw = " ".join(part for part in (date_value, time_value) if part)
        if not raw:
            return None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                return datetime.strptime(raw, fmt).replace(tzinfo=UTC)
            except ValueError:
                continue
        return None

    @staticmethod
    def _nested_name(data: Any) -> str:
        if not isinstance(data, dict):
            return ""
        for key in ("nombre", "descripcion"):
            value = str(data.get(key) or "")
            if value.strip():
                return CordobaConnector._clean_text(value)
        return ""

    @staticmethod
    def _clean_text(value: str) -> str:
        return " ".join(value.split()).strip()

    def _build_detail_url(self, value: Any) -> str:
        detail_id = self._clean_text(str(value or ""))
        if not detail_id:
            return f"{self.base_url}/#/compras-publicas/listadocompras/TODOS?e=ACTIVAS"
        return f"{self.base_url}/apifg/compra/compra/proveedor/{detail_id}"
