from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.matching import calculate_match


def make_tender(**overrides):
    base = {
        "title": "Adquisición de equipamiento hospitalario y monitores",
        "description_raw": "Compra de monitores multiparamétricos para terapia intensiva.",
        "organization": "Ministerio de Salud Pública",
        "procedure_type": "Licitación Pública",
        "jurisdiction": "Provincia de Corrientes",
        "estimated_amount": Decimal("25000000"),
        "publication_date": date.today(),
        "deadline_date": datetime.now(tz=UTC) + timedelta(days=10),
        "enrichments": [],
        "documents": [],
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def make_profile(**overrides):
    base = {
        "company_description": "Proveedor de equipamiento médico, monitores, descartables e insumos hospitalarios.",
        "include_keywords": ["monitor", "equipamiento hospitalario", "terapia intensiva"],
        "exclude_keywords": ["limpieza", "seguridad privada"],
        "jurisdictions": ["Provincia de Corrientes"],
        "preferred_buyers": ["Ministerio de Salud"],
        "sectors": ["salud", "equipamiento médico"],
        "min_amount": Decimal("1000000"),
        "max_amount": Decimal("50000000"),
    }
    base.update(overrides)
    return SimpleNamespace(**base)


class MatchingTests(unittest.TestCase):
    def test_high_score_when_profile_fits_title_buyer_and_jurisdiction(self) -> None:
        result = calculate_match(make_tender(), make_profile())

        self.assertGreaterEqual(float(result.score), 70)
        self.assertEqual(result.score_band, "high")
        self.assertTrue(result.reasons_json["components"]["preferred_buyers"]["hits"])

    def test_excluded_keywords_and_urgent_deadline_reduce_score(self) -> None:
        tender = make_tender(
            title="Servicio de limpieza integral para hospital",
            description_raw="Contratación de limpieza y mantenimiento general.",
            deadline_date=datetime.now(tz=UTC) + timedelta(hours=8),
            publication_date=date.today() - timedelta(days=5),
        )
        profile = make_profile(include_keywords=["hospital"], exclude_keywords=["limpieza"])

        result = calculate_match(tender, profile)

        self.assertLess(float(result.score), 45)
        self.assertEqual(result.score_band, "low")
        self.assertIn("limpieza", [hit.lower() for hit in result.reasons_json["components"]["negative_keywords"]["hits"]])

    def test_old_publication_without_other_signals_stays_low(self) -> None:
        tender = make_tender(
            title="Servicio administrativo general",
            description_raw="Tarea administrativa sin relación con el perfil.",
            organization="Ministerio de Hacienda",
            jurisdiction="Provincia de Salta",
            publication_date=date.today() - timedelta(days=250),
        )
        profile = make_profile(
            include_keywords=["monitor"],
            jurisdictions=["Provincia de Corrientes"],
            preferred_buyers=["Ministerio de Salud"],
            sectors=["equipamiento médico"],
        )

        result = calculate_match(tender, profile)

        self.assertLess(float(result.score), 30)
        self.assertEqual(result.score_band, "low")


if __name__ == "__main__":
    unittest.main()
