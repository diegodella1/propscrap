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


if __name__ == "__main__":
    unittest.main()
