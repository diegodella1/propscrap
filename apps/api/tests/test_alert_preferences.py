from __future__ import annotations

from pathlib import Path
import sys
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.alerts import _get_effective_alert_preferences
from app.services.company_profiles import normalize_company_alert_preferences
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

    def test_company_alert_preferences_normalize_deadline_offsets(self) -> None:
        preferences = normalize_company_alert_preferences(
            {
                "min_score": "70",
                "receive_relevant": True,
                "receive_deadlines": True,
                "deadline_only_for_saved": True,
                "deadline_offsets_hours": [24, "72", 168, 24, "bad"],
            }
        )

        self.assertEqual(preferences["min_score"], 70)
        self.assertEqual(preferences["deadline_offsets_hours"], [168, 72, 24])

    def test_effective_preferences_use_company_floor_and_saved_deadlines(self) -> None:
        user = SimpleNamespace(
            alert_preferences_json={
                "min_score": 50,
                "channels": ["dashboard", "whatsapp"],
                "receive_relevant": True,
                "receive_deadlines": True,
            }
        )

        preferences = _get_effective_alert_preferences(
            user,
            company_preferences={
                "min_score": 80,
                "receive_relevant": True,
                "receive_deadlines": True,
                "deadline_only_for_saved": True,
                "deadline_offsets_hours": [72, 24],
            },
        )

        self.assertEqual(preferences["min_score"], 80)
        self.assertTrue(preferences["deadline_only_for_saved"])
        self.assertEqual(preferences["deadline_offsets_hours"], [72, 24])
        self.assertEqual(preferences["channels"], ["dashboard", "whatsapp"])


if __name__ == "__main__":
    unittest.main()
