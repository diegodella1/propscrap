from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(__file__))
API_DIR = os.path.join(ROOT, "apps", "api")
if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)

from app.services.connectors.gcba import GcbaConnector


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extrae licitaciones GCBA desde un HTML o HAR local y guarda un JSON staged para ingestión."
    )
    parser.add_argument("--html", help="Ruta al HTML guardado de ListarAperturaProxima.aspx")
    parser.add_argument("--har", help="Ruta al HAR capturado de buenosairescompras.gob.ar")
    parser.add_argument(
        "--output",
        default=os.path.join(ROOT, "data", "staging", "gcba.json"),
        help="Ruta del JSON staged de salida",
    )
    parser.add_argument(
        "--detail-html-dir",
        help="Directorio opcional con fichas ciudadanas guardadas como HTML para enriquecer monto, objeto y fechas",
    )
    return parser.parse_args()


def load_listing_html(*, html_path: str | None = None, har_path: str | None = None) -> str:
    if html_path:
        return Path(html_path).read_text(encoding="utf-8")
    if har_path:
        payload = json.loads(Path(har_path).read_text(encoding="utf-8"))
        entries = payload.get("log", {}).get("entries", [])
        for entry in entries:
            request_url = str(entry.get("request", {}).get("url") or "")
            content = entry.get("response", {}).get("content", {})
            text = content.get("text")
            if (
                request_url.startswith("https://www.buenosairescompras.gob.ar/ListarAperturaProxima.aspx")
                and isinstance(text, str)
                and "ctl00_CPH1_GridListaPliegos" in text
            ):
                return text
        raise ValueError("No se encontró HTML útil de ListarAperturaProxima.aspx dentro del HAR")
    raise ValueError("Tenés que pasar html_path o har_path")


def _load_html(args: argparse.Namespace) -> str:
    return load_listing_html(html_path=args.html, har_path=args.har)


def export_gcba_json(
    *,
    html_path: str | None = None,
    har_path: str | None = None,
    output_path: str,
    detail_html_dir: str | None = None,
) -> int:
    connector = GcbaConnector()
    html = load_listing_html(html_path=html_path, har_path=har_path)
    records = connector._extract_rows(html)
    details = _detail_index(detail_html_dir)

    exported: list[dict[str, object]] = []
    for record in records:
        current = record
        if record.external_id and record.external_id in details:
            detail_html = details[record.external_id].read_text(encoding="utf-8")
            detail_record = connector.extract_detail_summary(detail_html, record.source_url)
            current = GcbaConnector._merge_records(record, detail_record)

        exported.append(
            {
                "external_id": current.external_id,
                "title": current.title,
                "description_raw": current.description_raw,
                "organization": current.organization,
                "jurisdiction": current.jurisdiction,
                "procedure_type": current.procedure_type,
                "publication_date": current.publication_date.isoformat() if current.publication_date else None,
                "deadline_date": current.deadline_date.isoformat() if current.deadline_date else None,
                "opening_date": current.opening_date.isoformat() if current.opening_date else None,
                "estimated_amount": str(current.estimated_amount) if current.estimated_amount is not None else None,
                "currency": current.currency,
                "source_url": current.source_url,
                "status_raw": current.status_raw,
            }
        )

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": connector.slug,
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "records": exported,
    }
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(exported)


def print_export_result(output_path: str, records_exported: int) -> None:
    print(f"Exported {records_exported} GCBA records to {output_path}")


def _detail_index(detail_dir: str | None) -> dict[str, Path]:
    if not detail_dir:
        return {}
    root = Path(detail_dir)
    if not root.exists():
        raise ValueError(f"El directorio de detalle no existe: {root}")
    return {path.stem: path for path in root.glob("*.html")}


def main() -> None:
    args = _parse_args()
    exported = export_gcba_json(
        html_path=args.html,
        har_path=args.har,
        output_path=args.output,
        detail_html_dir=args.detail_html_dir,
    )
    print_export_result(args.output, exported)


if __name__ == "__main__":
    main()
