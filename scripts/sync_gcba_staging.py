from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
API_DIR = os.path.join(ROOT, "apps", "api")
if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)

from app.db.session import SessionLocal
from app.jobs.ingest_source import ingest_source
from export_gcba_json import export_gcba_json, print_export_result


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera el staged JSON de GCBA desde HAR/HTML y opcionalmente lo ingiere."
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
        help="Directorio opcional con fichas ciudadanas guardadas como HTML para enriquecer los registros",
    )
    parser.add_argument(
        "--skip-ingest",
        action="store_true",
        help="Solo exporta el JSON staged y no ejecuta ingestión",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    records_exported = export_gcba_json(
        html_path=args.html,
        har_path=args.har,
        output_path=args.output,
        detail_html_dir=args.detail_html_dir,
    )
    print_export_result(args.output, records_exported)

    if args.skip_ingest:
        return

    os.environ["GCBA_STAGING_JSON_PATH"] = args.output
    db = SessionLocal()
    try:
        result = ingest_source(db, "licitaciones-caba")
    finally:
        db.close()
    print(result)


if __name__ == "__main__":
    main()
