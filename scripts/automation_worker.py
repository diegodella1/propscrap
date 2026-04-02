from __future__ import annotations

import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(__file__))
API_DIR = os.path.join(ROOT, "apps", "api")
if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)

from app.config import get_settings
from app.db.session import SessionLocal
from app.services.automation import run_automation_tick


def main() -> None:
    settings = get_settings()
    poll_seconds = max(settings.automation_poll_seconds, 30)

    while True:
        db = SessionLocal()
        try:
            result = run_automation_tick(db)
            print(result, flush=True)
        except Exception as exc:
            print({"status": "failed", "detail": str(exc)}, flush=True)
        finally:
            db.close()
        time.sleep(poll_seconds)


if __name__ == "__main__":
    main()
