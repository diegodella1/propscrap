from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
API_DIR = os.path.join(ROOT, "apps", "api")
if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)

from app.db.session import SessionLocal
from app.jobs.dispatch_alerts import run_alert_dispatch


def main() -> None:
    db = SessionLocal()
    try:
        result = run_alert_dispatch(db)
        print(result)
    finally:
        db.close()


if __name__ == "__main__":
    main()
