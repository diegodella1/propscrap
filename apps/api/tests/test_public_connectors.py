from __future__ import annotations

import unittest

from app.services.connectors.arsat import ArsatConnector
from app.services.connectors.catamarca import CatamarcaConnector
from app.services.connectors.chaco import ChacoConnector
from app.services.connectors.cordoba import CordobaConnector
from app.services.connectors.corrientes import CorrientesConnector
from app.services.connectors.inta import IntaConnector
from app.services.connectors.mendoza import MendozaConnector
from app.services.connectors.pami import PamiConnector
from app.services.connectors.rio_negro import RioNegroConnector
from app.services.connectors.salta import SaltaConnector
from app.services.connectors.san_luis import SanLuisConnector
from app.services.connectors.santa_fe import SantaFeConnector
from app.services.connectors.tucuman import TucumanConnector


class PublicConnectorTests(unittest.TestCase):
    def test_mendoza_extract_rows(self) -> None:
        html = """
        <table>
          <tr>
            <th>Número de Proceso</th><th>Nombre descriptivo de Proceso</th><th>Tipo de Procedimiento</th><th>Fecha de Apertura</th><th>Organismo</th>
          </tr>
          <tr>
            <td><a href="/detalle/1">10606-0012-LPU26</a></td>
            <td>Adquisición de insumos hospitalarios</td>
            <td>Licitación Pública</td>
            <td>14/04/2026 10:30</td>
            <td>Ministerio de Salud</td>
          </tr>
        </table>
        """
        items = MendozaConnector()._extract_rows(html)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].external_id, "10606-0012-LPU26")
        self.assertEqual(items[0].organization, "Ministerio de Salud")
        self.assertIn("/detalle/1", items[0].source_url)

    def test_salta_extract_records(self) -> None:
        html = """
        <div>
          Fecha/Hora Apertura: 23/04/2026 - 11:00 Licitación Pública N° 21/2026
          Objeto: Contratación del servicio de limpieza.
          Organismo Originante y Destino: Aguas del Norte
          Expte.: 0000000-27796/2026-0
        </div>
        """
        items = SaltaConnector()._extract_records(html)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].external_id, "0000000-27796/2026-0")
        self.assertEqual(items[0].procedure_type, "Licitación Pública")

    def test_chaco_extract_rows(self) -> None:
        html = """
        <table>
          <tr>
            <th>Número de Licitación</th><th>Nombre descriptivo de Proceso</th><th>Tipo de Licitación</th><th>Fecha de Apertura</th>
          </tr>
          <tr>
            <td><a href="/organismos/28/licitaciones/2026/245">245</a></td>
            <td>SERVICIO DE REPARACION</td>
            <td>Licitación Privada</td>
            <td>13/03/2026</td>
          </tr>
        </table>
        """
        items = ChacoConnector()._extract_rows(html)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].external_id, "245")
        self.assertIn("/organismos/28/licitaciones/2026/245", items[0].source_url)

    def test_arsat_extract_records(self) -> None:
        html = """
        <div>
          <h2>Licitación Privada N° 02/2025 - PROVISION 4 SWITCHES</h2>
          <p>Recepción de ofertas hasta el día 23/12/2025 a las 10.30 horas.</p>
          <p>Acto de Apertura de ofertas el día 23/12/2025 a las 11.00 horas.</p>
        </div>
        """
        items = ArsatConnector()._extract_records(html)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].external_id, "02/2025")
        self.assertEqual(items[0].organization, "ARSAT")

    def test_santa_fe_extract_records(self) -> None:
        payload = {
            "success": True,
            "data": [
                {
                    "idGestion": "137345",
                    "tipoGestion": "LICITACIÓN ACELERADA",
                    "tipoModalidad": "Sin Modalidad",
                    "fechaHoraApertura": "13-04-2026",
                    "fechaHoraAperturaFija": "2026-04-13 09:30:00",
                    "numeroAño": "21-2026",
                    "objeto": "LABORATORIO - INSUMOS DE HEMATOLOGIA",
                    "objetoCompleto": "LABORATORIO - INSUMOS DE HEMATOLOGIA",
                    "comprador": "HOSPITAL CENTENARIO ROSARIO",
                }
            ],
            "totalRecords": "1",
        }
        items = SantaFeConnector()._extract_records(payload)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].external_id, "21/2026")
        self.assertEqual(items[0].organization, "HOSPITAL CENTENARIO ROSARIO")
        self.assertIn("gestion.php?idGestion=137345", items[0].source_url)

    def test_pami_extract_records(self) -> None:
        html = """
        <div>
          <h1>Calendario de Aperturas</h1>
          <p>10/04/2026 11:00 Compulsa Abreviada 306/26 Un (1) Implante coclear marca MED EL modelo SYNCHRONY 2 FLEX 28 con procesador RONDO 3 en oído Izquierdo. remove_red_eye</p>
          <p>13/04/2026 10:00 Compulsa Abreviada 301/26 Provisión, logística y dispensa del principio activo importado: PATISIRAN (MARCA COMERCIAL ONPATTRO) remove_red_eye</p>
          <p>Volver</p>
        </div>
        """
        items = PamiConnector()._extract_records(html)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].external_id, "306/26")
        self.assertEqual(items[0].procedure_type, "Compulsa Abreviada")
        self.assertIn("Implante coclear", items[0].title)
        self.assertEqual(items[1].external_id, "301/26")
        self.assertIn("PATISIRAN", items[1].title)

    def test_inta_extract_records(self) -> None:
        payload = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 5265,
                    "fk_tender_type": "Contratación Directa",
                    "solicited_unit": "Unidad Central",
                    "categories": "Otros bienes de consumo",
                    "opening_place": "Rivadavia 1439, CABA",
                    "opening_date": "2099-04-16T11:30:00-03:00",
                    "limit_date": "2099-04-16T11:00:00-03:00",
                    "internal_procedure": "EX-2099-35716284-APN-GCYCE#INTA",
                    "tender_object": "Adquisición de materiales sanitarios.",
                    "state_name": "INICIADA",
                }
            ],
        }
        items = IntaConnector()._extract_records(payload)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].external_id, "EX-2099-35716284-APN-GCYCE#INTA")
        self.assertEqual(items[0].organization, "Unidad Central")
        self.assertEqual(items[0].procedure_type, "Contratación Directa")
        self.assertIn("/#/contrataciones/5265", items[0].source_url)

    def test_catamarca_extract_rows(self) -> None:
        html = """
        <table id="ctl00_CPH1_GridListaPliegosAperturaProxima">
          <tr>
            <th>Número de Proceso</th><th>Nombre descriptivo de Proceso</th><th>Tipo de Proceso</th><th>Fecha de Apertura</th><th>Estado</th><th>Unidad Ejecutora</th><th>Servicio Administrativo Financiero</th>
          </tr>
          <tr>
            <td><a href="javascript:__doPostBack('x','')">11-0002-CDI26</a></td>
            <td>ADQUISICIÓN DE EQUIPOS INFORMÁTICOS PROGRAMA SUMAR+</td>
            <td><p>Contratación Directa</p></td>
            <td>15/04/2099 09:00 Hrs.</td>
            <td><p>Publicado</p></td>
            <td><p>11 - Dirección Provincial de Administración del Ministerio de Salud</p></td>
            <td><p>11 - Dirección Provincial de Administración del Ministerio de Salud</p></td>
          </tr>
        </table>
        """
        items = CatamarcaConnector()._extract_rows(html)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].external_id, "11-0002-CDI26")
        self.assertEqual(items[0].procedure_type, "Contratación Directa")
        self.assertIn("SUMAR+", items[0].title)

    def test_san_luis_extract_rows(self) -> None:
        html = """
        <table class="apexir_WORKSHEET_DATA">
          <tr>
            <th></th><th>Proceso</th><th>Expediente</th><th>Jurisdicción</th><th>Objeto de Gasto</th><th>Ubicación</th><th>Tipo de Contratación</th><th>Cierre</th>
          </tr>
          <tr>
            <td><a href="f&#x3F;p&#x3D;2800&#x3A;401&#x3A;0&#x3A;&#x3A;NO&#x3A;401&#x3A;P401_COMCON_ID&#x3A;356824">ver</a></td>
            <td>1187/2026</td>
            <td>0000-2025-11100029</td>
            <td>MINISTERIO DE SEGURIDAD</td>
            <td>FORRAJES Y AGROQUIMICOS</td>
            <td>JUAN MARTIN DE PUEYRREDON - SAN LUIS</td>
            <td>LICITACION PUBLICA</td>
            <td>27/04/2099 10:30:00</td>
          </tr>
        </table>
        """
        items = SanLuisConnector()._extract_rows(html)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].external_id, "1187/2026")
        self.assertEqual(items[0].organization, "MINISTERIO DE SEGURIDAD")
        self.assertIn("P401_COMCON_ID:356824", items[0].source_url)

    def test_rio_negro_extract_rows(self) -> None:
        html = """
        <table id="ctl00_CPH1_GridListaPliegos">
          <tr>
            <th>Número de Proceso</th><th>Nombre descriptivo de Proceso</th><th>Tipo de Proceso</th><th>Fecha de Apertura</th><th>Estado</th><th>Unidad Ejecutora</th><th>Servicio Administrativo Financiero</th>
          </tr>
          <tr>
            <td><a href="javascript:__doPostBack('x','')">107-0004-CDI26</a></td>
            <td>Adquisición de Artículos de Limpieza</td>
            <td><p>Contratación Directa</p></td>
            <td>08/04/2099 08:30 Hrs.</td>
            <td><p>En Evaluacion</p></td>
            <td><p>Secretaría de Administración</p></td>
            <td><p>Ministerio de Modernización</p></td>
          </tr>
        </table>
        """
        items = RioNegroConnector()._extract_rows(html)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].external_id, "107-0004-CDI26")
        self.assertEqual(items[0].organization, "Secretaría de Administración")
        self.assertEqual(items[0].status_raw, "En Evaluacion")

    def test_cordoba_extract_records(self) -> None:
        payload = {
            "success": True,
            "compras": [
                {
                    "id": 288,
                    "nombre_compra": {
                        "nombre_compra": "CONCURSO",
                        "nombre": "CONCURSO DE PRECIOS",
                        "descripcion": None,
                    },
                    "titulo": "2025/116",
                    "objeto": "MATERIAL DE ACONDICIONAMIENTO PARA USO FARMACEUTICO - ALUMINIO",
                    "fecha_publicacion": "2099-03-25 15:11:47",
                    "estado": {"estado_compra": "PRORROGADO", "nombre": "Prorrogado"},
                    "expediente": "578-009649/2025",
                    "subentidad": {"id": 9285, "nombre": "SECRETARÍA DE SALUD"},
                    "entidad": {"id": "71", "nombre": "PODER EJECUTIVO MUNICIPAL"},
                    "tipo": {"tipo_compra": "CONCURSO", "nombre": "CONCURSO"},
                    "ultimo_llamado": {
                        "id": 1225,
                        "fecha_desde": "2099-04-14",
                        "hora_desde": "10:00:00",
                    },
                }
            ],
            "cantidad_paginas": 2,
        }
        items = CordobaConnector()._extract_records(payload)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].external_id, "2025/116")
        self.assertEqual(items[0].procedure_type, "CONCURSO DE PRECIOS")
        self.assertEqual(items[0].organization, "PODER EJECUTIVO MUNICIPAL")
        self.assertIn("SECRETARÍA DE SALUD", items[0].description_raw or "")
        self.assertIn("/apifg/compra/compra/proveedor/288", items[0].source_url)

    def test_tucuman_extract_rows(self) -> None:
        html = """
        <div class="modal fade" id="myModal8431" role="dialog">
          <div class="modal-dialog">
            <div class="modal-content modal-detalle">
              <div align="center">
                <p style="text-align: center;" align="center"><b>MINISTERIO DE SEGURIDAD - DEPARTAMENTO GENERAL DE POLICIA</b></p>
                <p style="background-color:#CCCCCC; width:70%; text-align: center; ">CONCURSO DE PRECIOS N&ordm; 78/2026</p>
                <table border="1">
                  <tr><td><b>RENGLON</b></td><td><b>DESCRIPCION</b></td></tr>
                  <tr><td>1</td><td>1 unidad de se adjunta listado de lo requerido y pliego y bases y condiciones particulares <br><b>-Rubro: REPUESTOS Y ACCESORIOS</b></td></tr>
                </table>
                <table width="400" border="0">
                  <tr><td bgcolor="#EEEEEE">Número de expediente:</td><td><b>195-196/219-T-2026</b></td></tr>
                  <tr><td bgcolor="#EEEEEE">Lugar:</td><td><b>Dirección de Administración Policía de Tucumán - Italia N° 2601 SM Tuc</b></td></tr>
                  <tr><td bgcolor="#EEEEEE">Fecha y hora</td><td><b>15/04/2099, 10:00:00</b></td></tr>
                </table>
                <a style="color:#990033 " href="#" onClick="window.open('http://rig.tucuman.gov.ar/obras_publicas/aplicacion/detalle_llamado.php?id_compra=8431',  '', 'width=570, height=650,scrollbars=yes')">Imprimir</a>
              </div>
            </div>
          </div>
        </div>
        """
        items = TucumanConnector()._extract_rows(html)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].external_id, "78/2026")
        self.assertEqual(items[0].procedure_type, "CONCURSO DE PRECIOS")
        self.assertEqual(items[0].organization, "MINISTERIO DE SEGURIDAD - DEPARTAMENTO GENERAL DE POLICIA")
        self.assertIn("195-196/219-T-2026", items[0].description_raw or "")
        self.assertIn("detalle_llamado.php?id_compra=8431", items[0].source_url)

    def test_corrientes_extract_records(self) -> None:
        payload = [
            {
                "doc_id": 1111,
                "titulo": "Licitación Pública Nº 03/ 26 - Convenio Marco- Ministerio De Desarrollo Social",
                "descripcion": "CONTRATACION DE UN SERVICIO DE PROVISION DE CARNES",
                "fecha_publicacion": "2099-04-08",
                "seleccion": "Licitaciones",
                "tipo_documento": "En curso",
            },
            {
                "doc_id": 1112,
                "titulo": "Pliego de Bases y Condiciones Particulares- Licitación Pública Nº 03/ 26 -",
                "descripcion": "",
                "fecha_publicacion": "2099-04-08",
                "seleccion": "Licitaciones",
                "tipo_documento": "En curso",
            },
        ]
        items = CorrientesConnector()._extract_records(payload)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].external_id, "03/26")
        self.assertEqual(items[0].organization, "Ministerio De Desarrollo Social")
        self.assertEqual(items[0].status_raw, "En curso")
        self.assertEqual(items[0].source_url, "https://www.cgpcorrientes.gov.ar/licitaciones-component")


if __name__ == "__main__":
    unittest.main()
