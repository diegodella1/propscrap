from __future__ import annotations

import os
import time
import sys

from sqlalchemy.exc import OperationalError

ROOT = os.path.dirname(os.path.dirname(__file__))
API_DIR = os.path.join(ROOT, "apps", "api")
if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)

from app.config import get_settings
from app.db.session import SessionLocal, engine
from app.jobs.match_tenders import match_all_tenders, match_tender


def main() -> None:
    settings = get_settings()
    retries = settings.matching_max_retries
    attempt = 0
    while True:
        db = SessionLocal()
        try:
            if len(sys.argv) > 1:
                result = match_tender(db, int(sys.argv[1]))
            else:
                result = match_all_tenders(db)
            print(result)
            return
        except OperationalError:
            attempt += 1
            engine.dispose()
            if attempt > retries:
                raise
            time.sleep(min(2 * attempt, 5))
        finally:
            db.close()


if __name__ == "__main__":
    main()
