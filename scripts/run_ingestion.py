from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
API_DIR = os.path.join(ROOT, "apps", "api")
if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)

from app.db.session import SessionLocal
from app.jobs.ingest_source import ingest_source


def main() -> None:
    source_slug = sys.argv[1] if len(sys.argv) > 1 else "comprar"
    db = SessionLocal()
    try:
        result = ingest_source(db, source_slug)
        print(result)
    finally:
        db.close()


if __name__ == "__main__":
    main()

