from __future__ import annotations

import unittest

from app.services.connectors.contratar import ContratarConnector


class ContratarConnectorTests(unittest.TestCase):
    def test_parse_csv_maps_official_columns(self) -> None:
        csv_text = """procedimiento_numero,procedimiento_nombre,uoc_codigo,uoc_descripcion,organismo_codigo_saf,organismo_nombre,expediente_procedimiento_numero,procedimiento_estado,procedimiento_objeto,procedimiento_tipo,solicitud_de_contratacion_numero,financiamiento_fuente_prev,sistema_contratacion,presupuesto_oficial_monto,pliego_condiciones_generales_numero_gedo,pliego_condiciones_particulares_numero_gedo,publicacion_contratar_fecha,publicacion_bora_fecha,publicacion_cantidad_dias,consultas_inicio_fecha,consultas_fin_fecha
452-0001-LPU17,Obra de prueba,452/0,UOC de prueba,328,328 - Secretaría de Energía,EE-10876,Adjudicado,Objeto de prueba,Licitación Pública,452-6-SCO17,1.5,Ajuste Alzado,596322129.52,PLIEG-1,PLIEG-2,2017-02-08 8:01:01,2017-02-08 8:00:00,15,2017-02-08 10:00:00,2017-03-08 23:59:00
"""
        connector = ContratarConnector()

        items = connector._parse_csv(csv_text)

        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item.external_id, "452-0001-LPU17")
        self.assertEqual(item.title, "Obra de prueba")
        self.assertEqual(item.organization, "328 - Secretaría de Energía")
        self.assertEqual(item.procedure_type, "Licitación Pública")
        self.assertEqual(item.publication_date.isoformat(), "2017-02-08")
        self.assertEqual(item.deadline_date.isoformat(), "2017-03-08T23:59:00+00:00")
        self.assertEqual(str(item.estimated_amount), "596322129.52")
        self.assertIn("numeroProceso=452-0001-LPU17", item.source_url)
        self.assertEqual(item.currency, "ARS")
        self.assertEqual(item.status_raw, "Adjudicado")
