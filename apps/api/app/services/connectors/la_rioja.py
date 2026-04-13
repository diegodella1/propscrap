from __future__ import annotations

from datetime import datetime
import re

from bs4 import BeautifulSoup
import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.http_safety import assert_public_https_url


class LaRiojaConnector(BaseConnector):
    slug = "licitaciones-la-rioja"
    name = "Provincia de La Rioja"
    base_url = "https://compras.larioja.gob.ar"
    page_url = "https://compras.larioja.gob.ar/avisos_gestion.php"
    search_url = "https://compras.larioja.gob.ar/avisosbuscar_gestion.php"

    def fetch(self) -> list[RawTenderRecord]:
        assert_public_https_url(self.search_url, label="la_rioja.search_url")
        settings = get_settings()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.post(
                self.search_url,
                data={
                    "nom": "",
                    "saf": "0",
                    "procedimiento": "0",
                    "apartado_directa": "0",
                    "modalidad": "0",
                    "expediente": "",
                },
            )
            response.raise_for_status()
            html = response.text
        return self._extract_rows(html)

    def _extract_rows(self, html: str) -> list[RawTenderRecord]:
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table", id="resultado")
        if table is None:
            raise ValueError("La Rioja procurement table not found")

        items: list[RawTenderRecord] = []
        for row in table.find_all("tr")[1:]:
            cells = row.find_all("td")
            if len(cells) < 7:
                continue

            organization = self._clean_text(cells[0].get_text(" ", strip=True))
            title = self._clean_text(cells[1].get_text(" ", strip=True))
            procedure_type = self._label_from_image(cells[2])
            modality = self._label_from_image(cells[3])
            deadline_date = self._parse_datetime(cells[4].get_text(" ", strip=True))
            detail_link = cells[6].find("a", href=True)
            source_url = self._extract_source_url(detail_link["href"]) if detail_link else self.page_url
            external_id = self._extract_external_id(source_url)

            if not external_id or not title:
                continue

            description = f"Modalidad: {modality}" if modality else None
            items.append(
                RawTenderRecord(
                    external_id=external_id,
                    title=title,
                    description_raw=description,
                    organization=organization or None,
                    jurisdiction="Provincia de La Rioja",
                    procedure_type=procedure_type or None,
                    publication_date=deadline_date.date() if deadline_date else None,
                    deadline_date=deadline_date,
                    opening_date=deadline_date,
                    estimated_amount=None,
                    currency="ARS",
                    source_url=source_url,
                    status_raw="Convocatoria vigente",
                )
            )

        if not items:
            raise ValueError("La Rioja procurement rows not found")
        return items

    @staticmethod
    def _label_from_image(cell) -> str:
        image = cell.find("img")
        src = image.get("src", "") if image else ""
        filename = src.rsplit("/", 1)[-1].lower()
        mapping = {
            "proced_cont_dir.gif": "Contratación Directa",
            "proced_licit_pub.gif": "Licitación Pública",
            "proced_licit_priv.gif": "Licitación Privada",
            "modal_tram_sim.gif": "Trámite Simplificado",
            "modal_comp_comp.gif": "Compra Compulsiva",
            "modal_llave_mano.gif": "Llave en Mano",
            "modal_ord_compra.gif": "Orden de Compra Abierta",
            "modal_sin_mod.gif": "Sin modalidad",
        }
        return mapping.get(filename, "")

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.strptime(value.strip(), "%d.%m.%Y %H:%M")
        except ValueError:
            return None

    def _extract_source_url(self, href: str) -> str:
        return str(httpx.URL(self.base_url).join(href))

    @staticmethod
    def _extract_external_id(source_url: str) -> str | None:
        match = re.search(r"xxx2=(\d+)", source_url)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def _clean_text(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()
