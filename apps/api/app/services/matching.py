from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
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
    sections = build_matching_sections(tender)
    normalized_text = sections["full"]

    components: dict[str, dict] = {}
    score = 0.0

    positive_breakdown = weighted_keyword_points(profile.include_keywords or [], sections, title_points=9, body_points=5)
    score += positive_breakdown["points"]
    components["positive_keywords"] = positive_breakdown

    sector_breakdown = weighted_keyword_points(profile.sectors or [], sections, title_points=7, body_points=4)
    score += sector_breakdown["points"]
    components["sector_fit"] = sector_breakdown

    negative_breakdown = weighted_keyword_points(profile.exclude_keywords or [], sections, title_points=14, body_points=8)
    score -= negative_breakdown["points"]
    components["negative_keywords"] = {
        "points": -negative_breakdown["points"],
        "hits": negative_breakdown["hits"],
        "title_hits": negative_breakdown["title_hits"],
        "body_hits": negative_breakdown["body_hits"],
    }

    jurisdiction_points = 0
    if tender.jurisdiction and any(jurisdiction_matches(item, tender.jurisdiction) for item in (profile.jurisdictions or [])):
        jurisdiction_points = 12
    score += jurisdiction_points
    components["jurisdiction"] = {"points": jurisdiction_points, "value": tender.jurisdiction}

    buyer_breakdown = preferred_buyer_points(profile.preferred_buyers or [], sections)
    score += buyer_breakdown["points"]
    components["preferred_buyers"] = buyer_breakdown

    semantic_points = semantic_alignment_points(profile, normalized_text)
    score += semantic_points
    components["semantic_alignment"] = {"points": semantic_points}

    amount_points = 0
    amount_penalty = 0
    if tender.estimated_amount is not None:
        if profile.min_amount and tender.estimated_amount < profile.min_amount:
            amount_penalty = 10
        elif profile.max_amount and tender.estimated_amount > profile.max_amount:
            amount_penalty = 10
        else:
            amount_points = 8
    score += amount_points - amount_penalty
    components["amount_fit"] = {"points": amount_points - amount_penalty, "value": str(tender.estimated_amount) if tender.estimated_amount is not None else None}

    freshness_points = publication_freshness_points(tender.publication_date)
    score += freshness_points
    components["freshness"] = {"points": freshness_points, "value": tender.publication_date.isoformat() if tender.publication_date else None}

    timing_adjustment = timing_points(tender)
    score += timing_adjustment
    components["timing"] = {"points": timing_adjustment}

    bounded = max(0, min(100, round(score, 2)))
    score_band = "high" if bounded >= 70 else "medium" if bounded >= 45 else "low"

    reasons_json = {
        "components": components,
        "summary": build_reason_summary(components),
    }
    return MatchResult(score=Decimal(str(bounded)), score_band=score_band, reasons_json=reasons_json)


def build_matching_text(tender: Tender) -> str:
    return build_matching_sections(tender)["full"]


def build_matching_sections(tender: Tender) -> dict[str, str]:
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

    title = normalize_text(tender.title or "")
    description = normalize_text(tender.description_raw or "")
    organization = normalize_text(tender.organization or "")
    procedure = normalize_text(tender.procedure_type or "")
    jurisdiction = normalize_text(tender.jurisdiction or "")
    enriched = normalize_text("\n".join(enriched_bits))
    documents = normalize_text(document_text[:4000] if document_text else "")

    return {
        "title": title,
        "description": description,
        "organization": organization,
        "procedure": procedure,
        "jurisdiction": jurisdiction,
        "enriched": enriched,
        "documents": documents,
        "body": "\n".join(part for part in [description, procedure, jurisdiction, enriched, documents] if part),
        "full": "\n".join(part for part in [title, description, organization, procedure, jurisdiction, enriched, documents] if part),
    }


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().lower()


def keyword_hits(keywords: list[str], normalized_text: str) -> list[str]:
    hits = []
    for keyword in keywords:
        if normalize_text(keyword) in normalized_text:
            hits.append(keyword)
    return hits


def weighted_keyword_points(
    keywords: list[str],
    sections: dict[str, str],
    *,
    title_points: int,
    body_points: int,
) -> dict[str, object]:
    hits: list[str] = []
    title_hits: list[str] = []
    body_hits: list[str] = []
    points = 0

    title_zone = " ".join(part for part in [sections["title"], sections["organization"]] if part)
    body_zone = " ".join(part for part in [sections["body"]] if part)
    for keyword in keywords:
        normalized_keyword = normalize_text(keyword)
        if not normalized_keyword:
            continue
        if normalized_keyword in title_zone:
            hits.append(keyword)
            title_hits.append(keyword)
            points += title_points
        elif normalized_keyword in body_zone:
            hits.append(keyword)
            body_hits.append(keyword)
            points += body_points

    max_points = max(title_points * 3, body_points * 4)
    return {
        "points": min(max_points, points),
        "hits": hits,
        "title_hits": title_hits,
        "body_hits": body_hits,
    }


def jurisdiction_matches(profile_value: str, tender_value: str) -> bool:
    left = normalize_text(profile_value)
    right = normalize_text(tender_value)
    if not left or not right:
        return False
    return left == right or left in right or right in left


def preferred_buyer_points(preferred_buyers: list[str], sections: dict[str, str]) -> dict[str, object]:
    title_zone = " ".join(part for part in [sections["title"], sections["organization"]] if part)
    body_zone = sections["body"]
    organization_hits: list[str] = []
    body_hits: list[str] = []
    points = 0

    for buyer in preferred_buyers:
        normalized_buyer = normalize_text(buyer)
        if not normalized_buyer:
            continue
        if normalized_buyer in title_zone:
            organization_hits.append(buyer)
            points += 10
        elif normalized_buyer in body_zone:
            body_hits.append(buyer)
            points += 6

    return {
        "points": min(20, points),
        "hits": organization_hits + body_hits,
        "organization_hits": organization_hits,
        "body_hits": body_hits,
    }


def semantic_alignment_points(profile: CompanyProfile, normalized_text: str) -> int:
    profile_tokens = tokenize(
        " ".join(
            filter(
                None,
                [
                    profile.company_description,
                    " ".join(profile.include_keywords or []),
                    " ".join(profile.sectors or []),
                ],
            )
        )
    )
    tender_tokens = tokenize(normalized_text)
    if not profile_tokens or not tender_tokens:
        return 0

    overlap = len(profile_tokens & tender_tokens)
    base = min(len(profile_tokens), 16)
    ratio = overlap / base if base else 0
    return min(15, math.floor(ratio * 18))


def tokenize(value: str) -> set[str]:
    return {token for token in re.findall(r"[a-záéíóúñ]{4,}", normalize_text(value)) if token}


def timing_points(tender: Tender) -> int:
    if tender.deadline_date is None:
        return 0
    now = datetime.now(tz=UTC)
    delta = tender.deadline_date - now
    hours = delta.total_seconds() / 3600
    if hours < 0:
        return -18
    if hours <= 24:
        return -10
    if hours <= 72:
        return -6
    if hours <= 24 * 7:
        return -3
    return 0


def publication_freshness_points(publication_date: date | None) -> int:
    if publication_date is None:
        return 0
    age_days = (datetime.now(tz=UTC).date() - publication_date).days
    if age_days < 0:
        return 0
    if age_days <= 30:
        return 6
    if age_days <= 90:
        return 3
    if age_days > 180:
        return -6
    return 0


def build_reason_summary(components: dict) -> list[str]:
    summary = []
    if components["positive_keywords"]["hits"]:
        summary.append(
            f"Coincidencias positivas: {', '.join(components['positive_keywords']['hits'][:4])}"
        )
    if components["sector_fit"]["hits"]:
        summary.append(
            f"Rubro o sector alineado: {', '.join(components['sector_fit']['hits'][:3])}"
        )
    if components["negative_keywords"]["hits"]:
        summary.append(
            f"Penaliza por: {', '.join(components['negative_keywords']['hits'][:4])}"
        )
    if components["preferred_buyers"]["hits"]:
        summary.append(
            f"Comprador preferido detectado: {', '.join(components['preferred_buyers']['hits'][:2])}"
        )
    if components["jurisdiction"]["points"] > 0:
        summary.append("La jurisdicción coincide con el alcance comercial configurado.")
    if components["freshness"]["points"] > 0:
        summary.append("La publicación es reciente y conviene revisarla primero.")
    if components["timing"]["points"] < 0:
        summary.append("La fecha límite reduce prioridad por cercanía.")
    if not summary:
        summary.append("Match armado por similitud general entre la licitación y el perfil comercial.")
    return summary
