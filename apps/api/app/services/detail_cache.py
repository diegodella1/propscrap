from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.tender import Tender
from app.services.source_registry import CONNECTORS

RAW_DIR = Path(__file__).resolve().parents[4] / "data" / "sample_raw"


def cache_tender_detail_html(db: Session, tender: Tender) -> Tender:
    connector_cls = CONNECTORS.get(tender.source.slug)
    if connector_cls is None:
        return tender

    html = connector_cls().fetch_detail_html(tender.source_url)
    if not html:
        return tender

    source_dir = RAW_DIR / tender.source.slug
    source_dir.mkdir(parents=True, exist_ok=True)
    file_path = source_dir / f"tender_{tender.id}.html"
    file_path.write_text(html, encoding="utf-8")

    tender.detail_html_path = str(file_path)
    tender.detail_cached_at = datetime.now(tz=UTC)
    return tender

