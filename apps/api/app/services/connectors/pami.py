from __future__ import annotations

from datetime import UTC, datetime
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.http_safety import assert_public_https_url


class PamiConnector(BaseConnector):
    slug = "pami"
    name = "PAMI"
    base_url = "https://prestadores.pami.org.ar"
    page_url = "https://transparenciaactiva.pami.org.ar/compras-y-contrataciones/"
    calendar_url = "https://prestadores.pami.org.ar/result.php?c=7-1-1-3&par=1"
    files_url = "https://prestadores.pami.org.ar/includes/compras.php"

    def fetch(self) -> list[RawTenderRecord]:
        assert_public_https_url(self.calendar_url, label="pami.calendar_url")
        settings = get_settings()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.get(self.calendar_url)
            response.raise_for_status()
            html = response.text
            return self._extract_records(html, client=client)

    def _extract_records(self, html: str, client: httpx.Client | None = None) -> list[RawTenderRecord]:
        soup = BeautifulSoup(html, "lxml")
        table = self._find_calendar_table(soup)
        if table is not None:
            return self._extract_table_records(table, client=client)

        return self._extract_regex_records(soup.get_text("\n", strip=True))

    def _extract_table_records(self, table, client: httpx.Client | None = None) -> list[RawTenderRecord]:
        items: list[RawTenderRecord] = []
        seen_ids: set[str] = set()
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 4:
                continue

            date_text = self._clean_text(cells[0].get_text(" ", strip=True))
            time_text = self._clean_text(cells[1].get_text(" ", strip=True))
            procedure_block = self._clean_text(cells[2].get_text(" ", strip=True))
            title = self._clean_text(cells[3].get_text(" ", strip=True))

            procedure_type, external_id = self._split_procedure_block(procedure_block)
            opening_date = self._parse_datetime(f"{date_text} {time_text}")
            file_id = self._extract_file_id(cells[4] if len(cells) > 4 else None)
            source_url = self._resolve_file_link(file_id, client) or self.calendar_url

            if not external_id or not title or external_id in seen_ids:
                continue

            seen_ids.add(external_id)
            items.append(
                RawTenderRecord(
                    external_id=external_id,
                    title=title,
                    description_raw=procedure_block or None,
                    organization="PAMI",
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

        if not items:
            raise ValueError("PAMI calendar records not found")
        return items

    def _extract_regex_records(self, text: str) -> list[RawTenderRecord]:
        normalized = re.sub(r"\n{2,}", "\n", text)
        marker = "Calendario de Aperturas"
        if marker in normalized:
            normalized = normalized.split(marker, 1)[1]

        pattern = re.compile(
            r"(?P<opening>\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2})\s+"
            r"(?P<procedure>Licitación\s+[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+|Compulsa\s+[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+|Concurso\s+[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+|Contratación\s+[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)\s+"
            r"(?P<expediente>\d+/\d+)\s+"
            r"(?P<title>.+?)(?=\s+\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}\s+(?:Licitación|Compulsa|Concurso|Contratación)\s+|(?:\s+Volver)?$)",
            re.IGNORECASE | re.DOTALL,
        )

        items: list[RawTenderRecord] = []
        seen_ids: set[str] = set()
        for match in pattern.finditer(normalized):
            opening_date = self._parse_datetime(match.group("opening"))
            procedure = self._clean_text(match.group("procedure"))
            external_id = self._clean_text(match.group("expediente"))
            title = self._clean_text(match.group("title").replace("remove_red_eye", ""))
            if not external_id or not title or external_id in seen_ids:
                continue
            seen_ids.add(external_id)
            items.append(
                RawTenderRecord(
                    external_id=external_id,
                    title=title,
                    description_raw=procedure,
                    organization="PAMI",
                    jurisdiction="Nación",
                    procedure_type=procedure,
                    publication_date=opening_date.date() if opening_date else None,
                    deadline_date=opening_date,
                    opening_date=opening_date,
                    estimated_amount=None,
                    currency="ARS",
                    source_url=self.calendar_url,
                    status_raw="Apertura próxima",
                )
            )

        if not items:
            raise ValueError("PAMI calendar records not found")

        return items

    @staticmethod
    def _find_calendar_table(soup: BeautifulSoup):
        for table in soup.find_all("table"):
            headers = [re.sub(r"\s+", " ", th.get_text(" ", strip=True)).strip().lower() for th in table.find_all("th")]
            if headers[:5] == ["fecha", "hora", "n° tramite", "productos o servicios", "archivos del pliego"]:
                return table
            normalized_headers = [header.replace("nº", "n°").replace("deg", "°") for header in headers]
            if normalized_headers[:5] == ["fecha", "hora", "n° tramite", "productos o servicios", "archivos del pliego"]:
                return table
        return None

    @staticmethod
    def _split_procedure_block(value: str) -> tuple[str | None, str | None]:
        match = re.match(r"(?P<procedure>.+?)\s+(?P<external_id>\d+/\d+)$", value)
        if not match:
            return None, None
        return (
            PamiConnector._clean_text(match.group("procedure")) or None,
            PamiConnector._clean_text(match.group("external_id")) or None,
        )

    @staticmethod
    def _extract_file_id(cell) -> str | None:
        if cell is None:
            return None
        onclick_value = ""
        clickable = cell.find(attrs={"onclick": True})
        if clickable is not None:
            onclick_value = str(clickable.get("onclick") or "")
        if not onclick_value:
            onclick_value = cell.get("onclick") or ""
        match = re.search(r"verArchivos\('(\d+)'\)", onclick_value)
        return match.group(1) if match else None

    def _resolve_file_link(self, file_id: str | None, client: httpx.Client | None) -> str | None:
        if not file_id or client is None:
            return None
        try:
            response = client.post(self.files_url, data={"accion": "get_files()", "id_compra": file_id})
            response.raise_for_status()
        except Exception:
            return None

        soup = BeautifulSoup(response.text, "lxml")
        anchor = soup.find("a", href=True)
        if anchor is None:
            return None
        href = self._clean_text(anchor.get("href") or "")
        if not href:
            return None
        return urljoin(self.files_url, href)

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.strptime(value.strip(), "%d/%m/%Y %H:%M").replace(tzinfo=UTC)
        except ValueError:
            return None

    @staticmethod
    def _clean_text(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()
