from __future__ import annotations

from sqlalchemy.orm import Session

from app.errors import NotFoundError
from app.services.detail_cache import cache_tender_detail_html
from app.services.documents import (
    download_documents_for_tender,
    get_tender_with_documents,
    parse_detail_body_text,
    upsert_document_text,
)
from app.services.ocr import run_pdf_ocr
from app.services.text_extraction import extract_pdf_text


def process_tender(db: Session, tender_id: int) -> dict:
    tender = get_tender_with_documents(db, tender_id)
    if tender is None:
        raise NotFoundError(f"Tender not found: {tender_id}")

    cache_tender_detail_html(db, tender)
    parsed_body = parse_detail_body_text(tender)
    if parsed_body and (not tender.description_raw or len(tender.description_raw) < 120):
        tender.description_raw = parsed_body[:12000]

    documents = download_documents_for_tender(db, tender)

    processed_documents = 0
    extracted_documents = 0
    for document in documents:
        processed_documents += 1
        if document.download_status != "downloaded" or not document.file_path:
            continue

        extracted_text, extraction_status, text_length, confidence = extract_pdf_text(document.file_path)
        extraction_method = "native_pdf"
        if extraction_status in {"failed", "low_text"} or text_length < 200:
            ocr_text, ocr_status, ocr_length, ocr_confidence = run_pdf_ocr(document.file_path)
            if ocr_status in {"success", "low_text"} and ocr_length >= text_length:
                extracted_text = ocr_text
                extraction_status = ocr_status
                text_length = ocr_length
                confidence = ocr_confidence
                extraction_method = "ocr_tesseract"

        upsert_document_text(
            db,
            document,
            extraction_method=extraction_method,
            extraction_status=extraction_status,
            extracted_text=extracted_text,
            text_length=text_length,
            confidence_score=confidence,
        )
        if extraction_status in {"success", "low_text"}:
            extracted_documents += 1

    db.commit()
    return {
        "tender_id": tender.id,
        "documents_processed": processed_documents,
        "documents_with_text": extracted_documents,
    }
