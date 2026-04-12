from __future__ import annotations

from pathlib import Path
import sys
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.users import get_user_alert_preferences, normalize_alert_preferences


class AlertPreferencesTests(unittest.TestCase):
    def test_company_default_min_score_is_used_when_user_has_no_custom_min_score(self) -> None:
        user = SimpleNamespace(
            alert_preferences_json={
                "channels": ["dashboard"],
                "receive_relevant": True,
                "receive_deadlines": True,
            }
        )

        preferences = get_user_alert_preferences(user, default_min_score=0)

        self.assertEqual(preferences["min_score"], 0)

    def test_email_is_an_allowed_alert_channel(self) -> None:
        preferences = normalize_alert_preferences(
            {
                "min_score": 50,
                "channels": ["dashboard", "email"],
                "receive_relevant": True,
                "receive_deadlines": False,
            }
        )

        self.assertEqual(preferences["channels"], ["dashboard", "email"])


if __name__ == "__main__":
    unittest.main()
