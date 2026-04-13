from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
import math
from datetime import UTC, datetime
from pathlib import Path
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import httpx

from app.config import get_settings
from app.services.connectors.base import BaseConnector, RawTenderRecord
from app.services.http_safety import assert_public_https_url


class GcbaConnector(BaseConnector):
    slug = "licitaciones-caba"
    name = "GCBA"
    base_url = "https://www.buenosairescompras.gob.ar"
    page_url = "https://www.buenosairescompras.gob.ar/ListarAperturaProxima.aspx"
    detail_url_prefix = "https://www.buenosairescompras.gob.ar/PLIEGO/VistaPreviaPliegoCiudadano.aspx"
    repo_root = Path(__file__).resolve().parents[5]

    def fetch(self) -> list[RawTenderRecord]:
        assert_public_https_url(self.page_url, label="gcba.page_url")
        settings = get_settings()
        staged_items = self._fetch_from_staged_json(settings.gcba_staging_json_path)
        if staged_items:
            return staged_items
        browser_items = self._fetch_with_browser(settings)
        if browser_items:
            return browser_items
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.get(self.page_url)
            response.raise_for_status()
            html = response.text
        return self._extract_rows(html)

    def _fetch_from_staged_json(self, json_path: str | None) -> list[RawTenderRecord] | None:
        path_value = (json_path or "").strip()
        if not path_value:
            return None

        path = self._resolve_staged_path(path_value)
        if not path.exists():
            return None

        payload = json.loads(path.read_text(encoding="utf-8"))
        return self._extract_records_from_json_payload(payload)

    def _extract_records_from_json_payload(self, payload: object) -> list[RawTenderRecord]:
        if isinstance(payload, dict):
            raw_records = payload.get("records")
        else:
            raw_records = payload

        if not isinstance(raw_records, list):
            raise ValueError("GCBA staged JSON must be a list or an object with a 'records' list")

        items: list[RawTenderRecord] = []
        for entry in raw_records:
            if not isinstance(entry, dict):
                continue

            external_id = self._clean_text(str(entry.get("external_id") or ""))
            title = self._clean_text(str(entry.get("title") or ""))
            source_url = self._clean_text(str(entry.get("source_url") or self.page_url))
            if not external_id or not title:
                continue

            items.append(
                RawTenderRecord(
                    external_id=external_id,
                    title=title,
                    description_raw=self._string_or_none(entry.get("description_raw")),
                    organization=self._string_or_none(entry.get("organization")),
                    jurisdiction=self._string_or_none(entry.get("jurisdiction")) or "Ciudad Autónoma de Buenos Aires",
                    procedure_type=self._string_or_none(entry.get("procedure_type")),
                    publication_date=self._parse_date(entry.get("publication_date")),
                    deadline_date=self._parse_datetime_value(entry.get("deadline_date")),
                    opening_date=self._parse_datetime_value(entry.get("opening_date")),
                    estimated_amount=self._parse_amount(str(entry.get("estimated_amount") or "")),
                    currency=self._string_or_none(entry.get("currency")) or "ARS",
                    source_url=source_url,
                    status_raw=self._string_or_none(entry.get("status_raw")),
                )
            )

        if not items:
            raise ValueError("GCBA staged JSON did not contain valid records")
        return items

    @classmethod
    def _resolve_staged_path(cls, path_value: str) -> Path:
        path = Path(path_value)
        if path.is_absolute():
            return path
        repo_relative = cls.repo_root / path
        if repo_relative.exists():
            return repo_relative
        return Path.cwd() / path

    def _fetch_with_browser(self, settings) -> list[RawTenderRecord] | None:
        if not settings.gcba_browser_enabled:
            return None
        try:
            from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
            from playwright.sync_api import sync_playwright
        except ImportError:
            return None

        launch_kwargs: dict[str, object] = {
            "headless": True,
            "args": ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
        }
        executable = (settings.playwright_chromium_executable or "").strip()
        if executable:
            launch_kwargs["executable_path"] = executable

        records_by_id: dict[str, RawTenderRecord] = {}
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(**launch_kwargs)
            try:
                page = browser.new_page(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/147.0.0.0 Safari/537.36"
                    ),
                    locale="en-US",
                )
                page.goto(self.page_url, wait_until="domcontentloaded", timeout=settings.browser_timeout_ms)
                page.wait_for_selector("#ctl00_CPH1_GridListaPliegos", timeout=settings.browser_timeout_ms)

                html = page.content()
                first_page_items = self._extract_rows(html)
                for item in first_page_items:
                    if item.external_id:
                        records_by_id[item.external_id] = item

                total_results = self._extract_total_results(html)
                rows_per_page = max(1, len(first_page_items))
                total_pages = max(1, math.ceil(total_results / rows_per_page)) if total_results else 1

                for page_number in range(2, total_pages + 1):
                    with page.expect_navigation(wait_until="domcontentloaded", timeout=settings.browser_timeout_ms):
                        page.evaluate(
                            """([target, argument]) => {
                                window.__doPostBack(target, argument);
                            }""",
                            ["ctl00$CPH1$GridListaPliegos", f"Page${page_number}"],
                        )
                    page.wait_for_selector("#ctl00_CPH1_GridListaPliegos", timeout=settings.browser_timeout_ms)
                    html = page.content()
                    for item in self._extract_rows(html):
                        if item.external_id and item.external_id not in records_by_id:
                            records_by_id[item.external_id] = item
            except PlaywrightTimeoutError:
                if records_by_id:
                    return list(records_by_id.values())
                return None
            finally:
                browser.close()
        return list(records_by_id.values()) or None

    def fetch_detail_html(self, source_url: str) -> str | None:
        assert_public_https_url(source_url, label="gcba.detail_url")
        settings = get_settings()
        with httpx.Client(
            timeout=settings.connector_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.get(source_url)
            response.raise_for_status()
            if "Proceso de compra" not in response.text and "Información básica del proceso" not in response.text:
                return None
            return response.text

    def _extract_rows(self, html: str) -> list[RawTenderRecord]:
        soup = BeautifulSoup(html, "lxml")
        table = self._find_procurement_table(soup)
        if table is None:
            raise ValueError("GCBA procurement table not found")

        items: list[RawTenderRecord] = []
        for row in table.find_all("tr")[1:]:
            cells = row.find_all("td")
            if len(cells) < 6:
                continue

            external_id = self._clean_text(cells[0].get_text(" ", strip=True))
            title = self._clean_text(cells[1].get_text(" ", strip=True))
            procedure_type = self._clean_text(cells[2].get_text(" ", strip=True))
            opening_date = self._parse_datetime(cells[3].get_text(" ", strip=True))
            status_raw = self._clean_text(cells[4].get_text(" ", strip=True))
            organization = self._clean_text(cells[5].get_text(" ", strip=True))
            source_url = self._extract_detail_link(cells[0]) or self.page_url

            if not external_id or not title:
                continue

            items.append(
                RawTenderRecord(
                    external_id=external_id,
                    title=title,
                    description_raw=None,
                    organization=organization or None,
                    jurisdiction="Ciudad Autónoma de Buenos Aires",
                    procedure_type=procedure_type or None,
                    publication_date=opening_date.date() if opening_date else None,
                    deadline_date=opening_date,
                    opening_date=opening_date,
                    estimated_amount=None,
                    currency="ARS",
                    source_url=source_url,
                    status_raw=status_raw or None,
                )
            )

        if not items:
            raise ValueError("GCBA procurement rows not found")
        return items

    @staticmethod
    def _extract_total_results(html: str) -> int | None:
        match = re.search(r"Se han encontrado \((\d+)\) resultados", html, re.IGNORECASE)
        if not match:
            return None
        try:
            return int(match.group(1))
        except ValueError:
            return None

    def extract_detail_summary(self, html: str, source_url: str) -> RawTenderRecord:
        soup = BeautifulSoup(html, "lxml")
        title = self._find_labeled_value(soup, "Nombre del proceso de compra") or self._find_labeled_value(
            soup, "Nombre de proceso"
        )
        external_id = self._find_labeled_value(soup, "Número del proceso de compra") or self._find_labeled_value(
            soup, "Nº de proceso"
        )
        procedure_type = self._find_labeled_value(soup, "Procedimiento de selección")
        organization = self._find_labeled_value(soup, "Unidad Operativa de Adquisiciones")
        description_raw = self._find_labeled_value(soup, "Objeto de la contratación")
        opening_date = self._parse_datetime(
            self._find_labeled_value(soup, "Fecha y hora acto de apertura"),
            formats=(
                "%d/%m/%Y %H:%M:%S",
                "%d/%m/%Y %H:%M",
            ),
        )
        publication_date = self._parse_datetime(
            self._find_labeled_value(soup, "Fecha y hora estimada de publicación en el portal"),
            formats=(
                "%d/%m/%Y %H:%M:%S",
                "%d/%m/%Y %H:%M",
            ),
        )
        estimated_amount = self._parse_amount(self._find_labeled_value(soup, "Monto"))

        if not title or not external_id:
            raise ValueError("GCBA detail page missing core fields")

        return RawTenderRecord(
            external_id=external_id,
            title=title,
            description_raw=description_raw or None,
            organization=organization or None,
            jurisdiction="Ciudad Autónoma de Buenos Aires",
            procedure_type=procedure_type or None,
            publication_date=publication_date.date() if publication_date else None,
            deadline_date=opening_date,
            opening_date=opening_date,
            estimated_amount=estimated_amount,
            currency="ARS",
            source_url=source_url,
            status_raw=None,
        )

    @staticmethod
    def _merge_records(base: RawTenderRecord, detail: RawTenderRecord) -> RawTenderRecord:
        return RawTenderRecord(
            external_id=detail.external_id or base.external_id,
            title=detail.title or base.title,
            description_raw=detail.description_raw or base.description_raw,
            organization=detail.organization or base.organization,
            jurisdiction=detail.jurisdiction or base.jurisdiction,
            procedure_type=detail.procedure_type or base.procedure_type,
            publication_date=detail.publication_date or base.publication_date,
            deadline_date=detail.deadline_date or base.deadline_date,
            opening_date=detail.opening_date or base.opening_date,
            estimated_amount=detail.estimated_amount if detail.estimated_amount is not None else base.estimated_amount,
            currency=detail.currency or base.currency,
            source_url=detail.source_url or base.source_url,
            status_raw=base.status_raw or detail.status_raw,
        )

    @staticmethod
    def _find_procurement_table(soup: BeautifulSoup):
        for table in soup.find_all("table"):
            header = " ".join(th.get_text(" ", strip=True).lower() for th in table.find_all("th"))
            if (
                "número de proceso" in header
                and "nombre de proceso" in header
                and "fecha de apertura" in header
                and "unidad ejecutora" in header
            ):
                return table
        return None

    @staticmethod
    def _extract_detail_link(cell) -> str | None:
        anchor = cell.find("a")
        if anchor is None:
            return None
        href = (anchor.get("href") or "").strip()
        if not href or href.startswith("javascript:"):
            return None
        return urljoin(GcbaConnector.base_url, href)

    @staticmethod
    def _find_labeled_value(soup: BeautifulSoup, label: str) -> str | None:
        target = GcbaConnector._normalize_label(label)
        for node in soup.find_all(["td", "th", "strong", "b", "span", "div", "p"]):
            text = GcbaConnector._clean_text(node.get_text(" ", strip=True))
            if GcbaConnector._normalize_label(text) != target:
                continue
            sibling = node.find_next_sibling()
            while sibling is not None:
                value = GcbaConnector._clean_text(sibling.get_text(" ", strip=True))
                if value:
                    return value
                sibling = sibling.find_next_sibling()
            parent = node.parent
            if parent is not None:
                texts = [GcbaConnector._clean_text(child.get_text(" ", strip=True)) for child in parent.find_all(recursive=False)]
                if len(texts) >= 2:
                    for index, item in enumerate(texts[:-1]):
                        if GcbaConnector._normalize_label(item) == target:
                            return texts[index + 1] or None
        return None

    @staticmethod
    def _normalize_label(value: str) -> str:
        value = GcbaConnector._clean_text(value)
        return value.replace(":", "").replace("º", "o").replace("°", "o").lower()

    @staticmethod
    def _parse_datetime(value: str | None, formats: tuple[str, ...] | None = None) -> datetime | None:
        if not value:
            return None
        raw = re.sub(r"\s+", " ", value).strip()
        raw = raw.replace(" Hrs.", "").replace(" Hrs", "")
        for fmt in formats or ("%d/%m/%Y %H:%M",):
            try:
                return datetime.strptime(raw, fmt).replace(tzinfo=UTC)
            except ValueError:
                continue
        return None

    @staticmethod
    def _parse_amount(value: str | None):
        if not value:
            return None
        raw = value.replace("$", "").strip()
        raw = re.sub(r"[^0-9,.\-]", "", raw)
        if not raw:
            return None
        if "," in raw and "." in raw:
            raw = raw.replace(".", "").replace(",", ".")
        elif "," in raw:
            raw = raw.replace(",", ".")
        elif raw.count(".") > 1:
            whole, fractional = raw.rsplit(".", 1)
            raw = whole.replace(".", "") + "." + fractional
        if not raw:
            return None
        try:
            return Decimal(raw)
        except Exception:
            return None

    @staticmethod
    def _parse_date(value: object) -> date | None:
        if value is None:
            return None
        raw = str(value).strip()
        if not raw:
            return None
        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(raw, fmt).date()
            except ValueError:
                continue
        return None

    @staticmethod
    def _parse_datetime_value(value: object) -> datetime | None:
        if value is None:
            return None
        raw = str(value).strip()
        if not raw:
            return None
        normalized = raw.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalized)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
        except ValueError:
            pass
        return GcbaConnector._parse_datetime(
            raw,
            formats=(
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%d/%m/%Y %H:%M:%S",
                "%d/%m/%Y %H:%M",
            ),
        )

    @staticmethod
    def _string_or_none(value: object) -> str | None:
        if value is None:
            return None
        text = GcbaConnector._clean_text(str(value))
        return text or None

    @staticmethod
    def _clean_text(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()
