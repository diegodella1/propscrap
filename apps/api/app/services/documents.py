from __future__ import annotations

from base64 import b64decode
from datetime import UTC, datetime
from pathlib import Path
import re

from bs4 import BeautifulSoup
import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.models.tender import DocumentText, Tender, TenderDocument, TenderEnrichment

DOCUMENTS_DIR = Path(__file__).resolve().parents[4] / "data" / "documents"


def discover_documents_for_tender(db: Session, tender: Tender) -> list[TenderDocument]:
    if tender.source.slug != "boletin-oficial":
        return []

    existing = db.execute(
        select(TenderDocument).where(TenderDocument.tender_id == tender.id)
    ).scalars().all()
    if existing:
        return existing

    match = re.search(r"/detalleAviso/tercera/(\d+)/(\d{8})", tender.source_url)
    if not match:
        return []

    notice_id, publication_ymd = match.groups()
    source_url = f"{tender.source_url}#pdf"
    document = TenderDocument(
        tender_id=tender.id,
        document_type="aviso_pdf",
        filename=f"aviso_{notice_id}.pdf",
        source_url=source_url,
        download_status="pending",
    )
    db.add(document)
    db.flush()
    return [document]


def download_documents_for_tender(db: Session, tender: Tender) -> list[TenderDocument]:
    settings = get_settings()
    documents = discover_documents_for_tender(db, tender)

    if tender.source.slug != "boletin-oficial":
        return documents

    match = re.search(r"/detalleAviso/tercera/(\d+)/(\d{8})", tender.source_url)
    if not match:
        return documents

    notice_id, publication_ymd = match.groups()

    with httpx.Client(
        timeout=settings.connector_timeout_seconds,
        headers={"User-Agent": settings.user_agent},
        follow_redirects=True,
    ) as client:
        response = client.post(
            "https://www.boletinoficial.gob.ar/pdf/download_aviso",
            data={
                "nombreSeccion": "tercera",
                "idAviso": notice_id,
                "fechaPublicacion": publication_ymd,
            },
        )
        response.raise_for_status()
        payload = response.json()

    pdf_base64 = payload.get("pdfBase64")
    if not pdf_base64:
        for document in documents:
            document.download_status = "failed"
        return documents

    tender_dir = DOCUMENTS_DIR / tender.source.slug / str(tender.id)
    tender_dir.mkdir(parents=True, exist_ok=True)
    file_path = tender_dir / f"aviso_{notice_id}.pdf"
    file_path.write_bytes(b64decode(pdf_base64))

    for document in documents:
        document.file_path = str(file_path)
        document.download_status = "downloaded"
        document.downloaded_at = datetime.now(tz=UTC)

    return documents


def parse_detail_body_text(tender: Tender) -> str | None:
    if not tender.detail_html_path:
        return None

    detail_path = Path(tender.detail_html_path)
    if not detail_path.exists():
        return None

    html = detail_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")

    if tender.source.slug == "boletin-oficial":
        article = soup.find("article")
        return article.get_text("\n", strip=True) if article else None

    if tender.source.slug == "comprar":
        body = soup.find("form", id="aspnetForm")
        return body.get_text("\n", strip=True)[:8000] if body else None

    return soup.get_text("\n", strip=True)[:8000]


def get_tender_with_documents(db: Session, tender_id: int) -> Tender | None:
    return db.execute(
        select(Tender)
        .options(
            selectinload(Tender.source),
            selectinload(Tender.documents).selectinload(TenderDocument.texts),
            selectinload(Tender.enrichments),
            selectinload(Tender.matches),
        )
        .where(Tender.id == tender_id)
    ).scalar_one_or_none()


def upsert_document_text(
    db: Session,
    document: TenderDocument,
    *,
    extraction_method: str,
    extraction_status: str,
    extracted_text: str | None,
    text_length: int,
    confidence_score: float | None,
) -> DocumentText:
    existing = db.execute(
        select(DocumentText).where(DocumentText.tender_document_id == document.id)
    ).scalar_one_or_none()
    if existing:
        existing.extraction_method = extraction_method
        existing.extraction_status = extraction_status
        existing.extracted_text = extracted_text
        existing.text_length = text_length
        existing.confidence_score = confidence_score
        return existing

    text = DocumentText(
        tender_document_id=document.id,
        extraction_method=extraction_method,
        extraction_status=extraction_status,
        extracted_text=extracted_text,
        text_length=text_length,
        confidence_score=confidence_score,
    )
    db.add(text)
    return text
