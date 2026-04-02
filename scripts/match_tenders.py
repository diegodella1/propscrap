from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
API_DIR = os.path.join(ROOT, "apps", "api")
if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)

from app.db.session import SessionLocal
from app.jobs.match_tenders import match_all_tenders, match_tender


def main() -> None:
    db = SessionLocal()
    try:
        if len(sys.argv) > 1:
            result = match_tender(db, int(sys.argv[1]))
        else:
            result = match_all_tenders(db)
        print(result)
    finally:
        db.close()


if __name__ == "__main__":
    main()
