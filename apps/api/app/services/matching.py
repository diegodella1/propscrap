from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
import math
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tender import CompanyProfile, Tender, TenderEnrichment, TenderMatch


@dataclass(slots=True)
class MatchResult:
    score: Decimal
    score_band: str
    reasons_json: dict


def match_tender_to_company(db: Session, tender: Tender, profile: CompanyProfile) -> TenderMatch:
    result = calculate_match(tender, profile)
    existing = db.execute(
        select(TenderMatch).where(
            TenderMatch.tender_id == tender.id,
            TenderMatch.company_profile_id == profile.id,
        )
    ).scalar_one_or_none()

    if existing is None:
        existing = TenderMatch(tender_id=tender.id, company_profile_id=profile.id)
        db.add(existing)

    existing.score = result.score
    existing.score_band = result.score_band
    existing.reasons_json = result.reasons_json
    existing.matched_at = datetime.now(tz=UTC)
    return existing


def calculate_match(tender: Tender, profile: CompanyProfile) -> MatchResult:
    text = build_matching_text(tender)
    normalized_text = normalize_text(text)

    components: dict[str, dict] = {}
    score = 0.0

    positive_hits = keyword_hits(profile.include_keywords or [], normalized_text)
    positive_points = min(35, len(positive_hits) * 7)
    score += positive_points
    components["positive_keywords"] = {"points": positive_points, "hits": positive_hits}

    negative_hits = keyword_hits(profile.exclude_keywords or [], normalized_text)
    negative_points = min(25, len(negative_hits) * 8)
    score -= negative_points
    components["negative_keywords"] = {"points": -negative_points, "hits": negative_hits}

    jurisdiction_points = 0
    if tender.jurisdiction and any(
        normalize_text(item) == normalize_text(tender.jurisdiction) for item in (profile.jurisdictions or [])
    ):
        jurisdiction_points = 15
    score += jurisdiction_points
    components["jurisdiction"] = {"points": jurisdiction_points, "value": tender.jurisdiction}

    buyer_points = 0
    buyer_hits = []
    organization = normalize_text(tender.organization or "")
    for buyer in profile.preferred_buyers or []:
        if normalize_text(buyer) in organization:
            buyer_hits.append(buyer)
    if buyer_hits:
        buyer_points = min(15, len(buyer_hits) * 8)
    score += buyer_points
    components["preferred_buyers"] = {"points": buyer_points, "hits": buyer_hits}

    semantic_points = semantic_alignment_points(profile, normalized_text)
    score += semantic_points
    components["semantic_alignment"] = {"points": semantic_points}

    amount_points = 0
    amount_penalty = 0
    if tender.estimated_amount is not None:
        if profile.min_amount and tender.estimated_amount < profile.min_amount:
            amount_penalty = 8
        elif profile.max_amount and tender.estimated_amount > profile.max_amount:
            amount_penalty = 8
        else:
            amount_points = 10
    score += amount_points - amount_penalty
    components["amount_fit"] = {"points": amount_points - amount_penalty, "value": str(tender.estimated_amount) if tender.estimated_amount is not None else None}

    timing_penalty = timing_points(tender)
    score += timing_penalty
    components["timing"] = {"points": timing_penalty}

    bounded = max(0, min(100, round(score, 2)))
    score_band = "high" if bounded >= 75 else "medium" if bounded >= 50 else "low"

    reasons_json = {
        "components": components,
        "summary": build_reason_summary(components),
    }
    return MatchResult(score=Decimal(str(bounded)), score_band=score_band, reasons_json=reasons_json)


def build_matching_text(tender: Tender) -> str:
    enrichment = tender.enrichments[0] if tender.enrichments else None
    enriched_bits = []
    if enrichment and enrichment.summary_structured_json:
        structured = enrichment.summary_structured_json
        enriched_bits.extend(structured.get("key_requirements") or [])
        enriched_bits.extend(structured.get("risk_flags") or [])
        if structured.get("procurement_object"):
            enriched_bits.append(structured["procurement_object"])
        if enrichment.summary_short:
            enriched_bits.append(enrichment.summary_short)

    document_text = ""
    for document in tender.documents:
        for text in document.texts:
            if text.extracted_text and text.text_length > 100:
                document_text = text.extracted_text
                break
        if document_text:
            break

    return "\n".join(
        filter(
            None,
            [
                tender.title,
                tender.description_raw,
                tender.organization,
                tender.procedure_type,
                tender.jurisdiction,
                "\n".join(enriched_bits),
                document_text[:4000] if document_text else "",
            ],
        )
    )


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().lower()


def keyword_hits(keywords: list[str], normalized_text: str) -> list[str]:
    hits = []
    for keyword in keywords:
        if normalize_text(keyword) in normalized_text:
            hits.append(keyword)
    return hits


def semantic_alignment_points(profile: CompanyProfile, normalized_text: str) -> int:
    profile_tokens = tokenize(profile.company_description)
    tender_tokens = tokenize(normalized_text)
    if not profile_tokens or not tender_tokens:
        return 0

    overlap = len(profile_tokens & tender_tokens)
    base = min(len(profile_tokens), 12)
    ratio = overlap / base if base else 0
    return min(20, math.floor(ratio * 20))


def tokenize(value: str) -> set[str]:
    return {token for token in re.findall(r"[a-záéíóúñ]{4,}", normalize_text(value)) if token}


def timing_points(tender: Tender) -> int:
    if tender.deadline_date is None:
        return 0
    now = datetime.now(tz=UTC)
    delta = tender.deadline_date - now
    hours = delta.total_seconds() / 3600
    if hours < 0:
        return -15
    if hours <= 24:
        return -12
    if hours <= 72:
        return -8
    if hours <= 24 * 7:
        return -4
    return 0


def build_reason_summary(components: dict) -> list[str]:
    summary = []
    if components["positive_keywords"]["hits"]:
        summary.append(
            f"Coincidencias positivas: {', '.join(components['positive_keywords']['hits'][:4])}"
        )
    if components["negative_keywords"]["hits"]:
        summary.append(
            f"Penaliza por: {', '.join(components['negative_keywords']['hits'][:4])}"
        )
    if components["preferred_buyers"]["hits"]:
        summary.append(
            f"Comprador preferido detectado: {', '.join(components['preferred_buyers']['hits'][:2])}"
        )
    if components["timing"]["points"] < 0:
        summary.append("La fecha límite reduce prioridad por cercanía.")
    return summary
