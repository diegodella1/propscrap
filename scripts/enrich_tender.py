from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
API_DIR = os.path.join(ROOT, "apps", "api")
if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)

from app.db.session import SessionLocal
from app.jobs.enrich_tender import enrich_tender


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: enrich_tender.py <tender_id>")

    tender_id = int(sys.argv[1])
    db = SessionLocal()
    try:
        result = enrich_tender(db, tender_id)
        print(result)
    finally:
        db.close()


if __name__ == "__main__":
    main()
