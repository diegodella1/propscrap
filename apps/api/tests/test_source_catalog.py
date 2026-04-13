from __future__ import annotations

import unittest

from app.services.source_catalog import SOURCE_CATALOG


class SourceCatalogTests(unittest.TestCase):
    def test_source_catalog_has_unique_slugs(self) -> None:
        slugs = [str(item["slug"]) for item in SOURCE_CATALOG]
        self.assertEqual(len(slugs), len(set(slugs)))

    def test_pdf_gap_sources_were_added(self) -> None:
        slugs = {str(item["slug"]) for item in SOURCE_CATALOG}
        expected = {
            "licitaciones-catamarca",
            "licitaciones-formosa",
            "licitaciones-jujuy",
            "licitaciones-la-rioja",
            "licitaciones-santiago-del-estero",
        }
        self.assertTrue(expected.issubset(slugs))

    def test_priority_sources_keep_verified_official_urls(self) -> None:
        catalog = {str(item["slug"]): item for item in SOURCE_CATALOG}
        self.assertEqual(
            catalog["licitaciones-santa-fe"]["base_url"],
            "https://www.santafe.gov.ar/gestionesdecompras/site/index.php?a=consultas.index",
        )
        self.assertEqual(catalog["licitaciones-mendoza"]["base_url"], "https://comprar.mendoza.gov.ar/")
        self.assertEqual(catalog["licitaciones-salta"]["base_url"], "https://compras.salta.gob.ar/")
        self.assertEqual(catalog["pami"]["base_url"], "https://transparenciaactiva.pami.org.ar/compras-y-contrataciones/")
        self.assertEqual(catalog["inta"]["base_url"], "https://compras.inta.gob.ar/")

    def test_recently_implemented_sources_are_active(self) -> None:
        catalog = {str(item["slug"]): item for item in SOURCE_CATALOG}
        self.assertTrue(catalog["licitaciones-san-juan"]["is_active"])
        self.assertEqual(catalog["licitaciones-san-juan"]["connector_slug"], "licitaciones-san-juan")
        self.assertTrue(catalog["licitaciones-la-rioja"]["is_active"])
        self.assertEqual(catalog["licitaciones-la-rioja"]["connector_slug"], "licitaciones-la-rioja")
        self.assertTrue(catalog["licitaciones-neuquen"]["is_active"])
        self.assertEqual(catalog["licitaciones-neuquen"]["connector_slug"], "licitaciones-neuquen")
        self.assertTrue(catalog["licitaciones-tierra-del-fuego"]["is_active"])
        self.assertEqual(catalog["licitaciones-tierra-del-fuego"]["connector_slug"], "licitaciones-tierra-del-fuego")

    def test_entre_rios_is_profiled_with_connector_but_stays_inactive(self) -> None:
        catalog = {str(item["slug"]): item for item in SOURCE_CATALOG}
        self.assertEqual(catalog["licitaciones-entre-rios"]["connector_slug"], "licitaciones-entre-rios")
        self.assertFalse(catalog["licitaciones-entre-rios"]["is_active"])
        self.assertTrue(catalog["licitaciones-entre-rios"]["config_json"]["implemented"])

    def test_gcba_is_implemented_via_staged_json_but_stays_inactive(self) -> None:
        catalog = {str(item["slug"]): item for item in SOURCE_CATALOG}
        self.assertEqual(catalog["licitaciones-caba"]["connector_slug"], "licitaciones-caba")
        self.assertEqual(catalog["licitaciones-caba"]["scraping_mode"], "staged_json")
        self.assertFalse(catalog["licitaciones-caba"]["is_active"])
        self.assertTrue(catalog["licitaciones-caba"]["config_json"]["implemented"])


if __name__ == "__main__":
    unittest.main()
