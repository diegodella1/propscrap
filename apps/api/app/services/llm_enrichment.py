from __future__ import annotations

from dataclasses import dataclass
import json

import httpx

from app.config import get_settings
from app.errors import ConfigurationError, ExternalServiceError


ENRICHMENT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "summary_short": {"type": "string"},
        "procurement_object": {"type": "string"},
        "key_dates": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "publication_date": {"type": ["string", "null"]},
                "deadline_date": {"type": ["string", "null"]},
                "opening_date": {"type": ["string", "null"]},
            },
            "required": ["publication_date", "deadline_date", "opening_date"],
        },
        "key_requirements": {"type": "array", "items": {"type": "string"}},
        "risk_flags": {"type": "array", "items": {"type": "string"}},
        "evidence_snippets": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "summary_short",
        "procurement_object",
        "key_dates",
        "key_requirements",
        "risk_flags",
        "evidence_snippets",
    ],
}

DEFAULT_MASTER_PROMPT = (
    "Analiza esta licitación de Argentina y devuelve solo JSON válido según el schema. "
    "Resume el objeto de compra, fechas, requisitos y riesgos de forma concisa y útil para ventas B2B."
)


@dataclass(slots=True)
class EnrichmentResult:
    model: str
    payload: dict


def enrich_tender_text(
    *,
    title: str,
    source_name: str,
    body_text: str,
    openai_api_key: str | None = None,
    openai_model: str | None = None,
    master_prompt: str | None = None,
) -> EnrichmentResult:
    settings = get_settings()
    resolved_api_key = (openai_api_key or settings.openai_api_key or "").strip()
    resolved_model = (openai_model or settings.openai_model).strip()
    resolved_prompt = (master_prompt or DEFAULT_MASTER_PROMPT).strip()
    if not settings.llm_enabled or not resolved_api_key:
        raise ConfigurationError("OPENAI_API_KEY not configured")

    prompt = (
        f"{resolved_prompt}\n\n"
        f"Fuente: {source_name}\n"
        f"Título: {title}\n\n"
        f"Texto:\n{body_text[:16000]}"
    )

    request_payload = {
        "model": resolved_model,
        "input": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Eres un analista de licitaciones. Devuelves únicamente JSON estricto, "
                            "sin markdown y sin texto adicional."
                        ),
                    }
                ],
            },
            {"role": "user", "content": [{"type": "input_text", "text": prompt}]},
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "tender_enrichment",
                "schema": ENRICHMENT_SCHEMA,
                "strict": True,
            }
        },
    }

    with httpx.Client(
        base_url="https://api.openai.com/v1",
        headers={
            "Authorization": f"Bearer {resolved_api_key}",
            "Content-Type": "application/json",
        },
        timeout=90,
    ) as client:
        try:
            response = client.post("/responses", json=request_payload)
            response.raise_for_status()
            payload = response.json()
        except httpx.HTTPError as exc:
            raise ExternalServiceError(f"OpenAI enrichment request failed: {exc}") from exc

    content = _extract_output_json(payload)
    return EnrichmentResult(model=resolved_model, payload=content)


def _extract_output_json(payload: dict) -> dict:
    for item in payload.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                try:
                    return json.loads(content["text"])
                except json.JSONDecodeError as exc:
                    raise ExternalServiceError("OpenAI returned invalid JSON for enrichment") from exc
    raise ExternalServiceError("Structured JSON output not found in OpenAI response")
