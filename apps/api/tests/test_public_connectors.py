from __future__ import annotations

import unittest

from bs4 import BeautifulSoup

from app.services.connectors.base import RawTenderRecord
from app.services.connectors.arsat import ArsatConnector
from app.services.connectors.banco_nacion import BancoNacionConnector
from app.services.connectors.catamarca import CatamarcaConnector
from app.services.connectors.chaco import ChacoConnector
from app.services.connectors.cnea import CneaConnector
from app.services.connectors.cordoba import CordobaConnector
from app.services.connectors.corrientes import CorrientesConnector
from app.services.connectors.entre_rios import EntreRiosConnector
from app.services.connectors.gcba import GcbaConnector
from app.services.connectors.inta import IntaConnector
from app.services.connectors.inti_public import IntiPublicConnector
from app.services.connectors.la_rioja import LaRiojaConnector
from app.services.connectors.mendoza import MendozaConnector
from app.services.connectors.nasa_nucleoelectrica import NasaNucleoelectricaConnector
from app.services.connectors.neuquen import NeuquenConnector
from app.services.connectors.pami import PamiConnector
from app.services.connectors.pbac import PbacConnector
from app.services.connectors.rio_negro import RioNegroConnector
from app.services.connectors.salta import SaltaConnector
from app.services.connectors.san_juan import SanJuanConnector
from app.services.connectors.san_luis import SanLuisConnector
from app.services.connectors.santa_fe import SantaFeConnector
from app.services.connectors.tierra_del_fuego import TierraDelFuegoConnector
from app.services.connectors.tucuman import TucumanConnector


class PublicConnectorTests(unittest.TestCase):
    def test_banco_nacion_extract_rows(self) -> None:
        html = """
        <table class="table table-bordered cotizador">
          <thead>
            <tr>
              <th>Informática</th><th>Artículo</th><th>Llamado</th><th></th><th>Valor Pliego (en $)</th><th>Fecha</th><th>Hora</th><th>Costo estimado s/IVA (en $)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Software</td>
              <td>Provisión de plataforma de observabilidad.</td>
              <td>CDS-1290/2026</td>
              <td><a href="/BackOffice/licitaciones/pliegos/92. Pliego Web LPU CDS 1290 2026 .pdf">Descargar</a></td>
              <td>0,0000</td>
              <td>26/12/2099</td>
              <td>12:0:0</td>
              <td>125.000.000,00</td>
            </tr>
          </tbody>
        </table>
        """
        items = BancoNacionConnector()._extract_rows(html)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].external_id, "CDS-1290/2026")
        self.assertEqual(items[0].organization, "Banco Nación")
        self.assertEqual(items[0].procedure_type, "Contratación de Servicios")
        self.assertEqual(
            items[0].source_url,
            "https://www.bna.com.ar/BackOffice/licitaciones/pliegos/92. Pliego Web LPU CDS 1290 2026 .pdf",
        )

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

    def test_mendoza_extract_rows_uses_public_detail_redirect(self) -> None:
        html = """
        <table>
          <tr>
            <th>Número de Proceso</th><th>Nombre descriptivo de Proceso</th><th>Tipo de Procedimiento</th><th>Fecha de Apertura</th><th>Organismo</th>
          </tr>
          <tr>
            <td><a onclick="return redireccionar('PLIEGO/VistaPreviaPliegoCiudadano.aspx?qs=abc123');" href="javascript:__doPostBack('x','')">11405-0037-CDI26</a></td>
            <td>Servicio de iluminación</td>
            <td>Contratación Directa</td>
            <td>14/04/2026 10:30</td>
            <td>Subsecretaría de Cultura</td>
          </tr>
        </table>
        """
        items = MendozaConnector()._extract_rows(html)
        self.assertEqual(len(items), 1)
        self.assertEqual(
            items[0].source_url,
            "https://comprar.mendoza.gov.ar/PLIEGO/VistaPreviaPliegoCiudadano.aspx?qs=abc123",
        )

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

    def test_arsat_extract_external_id_from_dash_pattern(self) -> None:
        title = "Licitación Pública Nacional N° 05/2025 - AMPLIACIÓN DE LA REFEFO EN EL LITORAL PATAGÓNICO"
        self.assertEqual(ArsatConnector()._extract_external_id(title), "05/2025")

    def test_arsat_extract_external_id_from_abbreviated_pattern(self) -> None:
        title = "01. LPri 02-2025 – Pliego de Condiciones Generales"
        self.assertEqual(ArsatConnector()._extract_external_id(title), "02/2025")

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

    def test_pami_extract_table_records(self) -> None:
        html = """
        <table class="tabla_compras">
          <tr>
            <th>Fecha</th><th>Hora</th><th>N&deg; Tramite</th><th>Productos o servicios</th><th>Archivos del pliego</th>
          </tr>
          <tr class="gris">
            <td class="center">13/04/2026</td>
            <td class="center">10:00</td>
            <td>Compulsa Abreviada 301/26</td>
            <td>Provisión, logística y dispensa del principio activo importado: PATISIRAN (MARCA COMERCIAL ONPATTRO)</td>
            <td class="center"><i class="material-icons active" onClick="verArchivos('624892');">remove_red_eye</i></td>
          </tr>
        </table>
        """
        items = PamiConnector()._extract_records(html)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].external_id, "301/26")
        self.assertEqual(items[0].procedure_type, "Compulsa Abreviada")
        self.assertIn("PATISIRAN", items[0].title)
        self.assertEqual(items[0].source_url, PamiConnector.calendar_url)

    def test_pami_extract_file_id(self) -> None:
        html = """
        <td class="center"><i class="material-icons active" onClick="verArchivos('624892');">remove_red_eye</i></td>
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "lxml")
        file_id = PamiConnector()._extract_file_id(soup.find("td"))
        self.assertEqual(file_id, "624892")

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

    def test_inti_extract_records_from_sitemap(self) -> None:
        xml = """
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
          <url>
            <loc>https://www.inti.gob.ar/assets/uploads/contrataciones/LP07_19.pdf</loc>
            <lastmod>2019-06-03T18:08:46+00:00</lastmod>
          </url>
          <url>
            <loc>https://www.inti.gob.ar/assets/uploads/contrataciones/Circular-LPNO-UCOFI01-18.pdf</loc>
            <lastmod>2018-10-08T18:57:31+00:00</lastmod>
          </url>
        </urlset>
        """
        items = IntiPublicConnector()._extract_records(xml)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].external_id, "LP07-19")
        self.assertEqual(items[0].organization, "INTI")
        self.assertEqual(items[0].procedure_type, "Licitación Pública")
        self.assertEqual(items[1].external_id, "Circular-LPNO-UCOFI01-18")
        self.assertEqual(items[1].procedure_type, "Licitación Pública Nacional")

    def test_nasa_nucleoelectrica_extract_records_from_boletin(self) -> None:
        html = """
        <html>
          <body>
            <h2>Edición del 13 de abril de 2026</h2>
            <a href="/detalleAviso/tercera/12345678/20260413">
              <div class="linea-aviso">
                <p class="item">NUCLEOELÉCTRICA ARGENTINA S.A.</p>
                <p class="item-detalle">Licitación Pública Nacional N° 03/2026 - Servicio integral de mantenimiento</p>
              </div>
            </a>
          </body>
        </html>
        """
        items = NasaNucleoelectricaConnector()._extract_records(html)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].external_id, "12345678")
        self.assertEqual(items[0].organization, "Nucleoeléctrica Argentina S.A.")
        self.assertEqual(items[0].procedure_type, "Licitación Pública")
        self.assertEqual(items[0].publication_date.isoformat(), "2026-04-13")
        self.assertEqual(
            items[0].source_url,
            "https://www.boletinoficial.gob.ar/detalleAviso/tercera/12345678/20260413",
        )

    def test_cnea_filters_records_from_public_portals(self) -> None:
        connector = CneaConnector()
        comprar_row = RawTenderRecord(
            external_id="105-0001-LPU26",
            title="Adquisición de insumos para laboratorio",
            description_raw=None,
            organization="Comisión Nacional de Energía Atómica",
            jurisdiction="Nación",
            procedure_type="Licitación Pública",
            publication_date=None,
            deadline_date=None,
            opening_date=None,
            estimated_amount=None,
            currency="ARS",
            source_url="https://comprar.gob.ar/proceso/1",
            status_raw="Publicada",
        )
        contratar_row = RawTenderRecord(
            external_id="76/2026",
            title="Obra complementaria",
            description_raw="Servicio Administrativo Financiero 105 | Centro Atómico Constituyentes",
            organization="Ministerio de Economía",
            jurisdiction="Nación",
            procedure_type="Licitación Pública",
            publication_date=None,
            deadline_date=None,
            opening_date=None,
            estimated_amount=None,
            currency="ARS",
            source_url="https://contratar.gob.ar/BuscarAvanzado.aspx?numeroProceso=76/2026",
            status_raw="Publicada",
        )
        unrelated_row = RawTenderRecord(
            external_id="999",
            title="Servicio ajeno",
            description_raw="Ministerio de Salud",
            organization="Ministerio de Salud",
            jurisdiction="Nación",
            procedure_type="Contratación Directa",
            publication_date=None,
            deadline_date=None,
            opening_date=None,
            estimated_amount=None,
            currency="ARS",
            source_url="https://comprar.gob.ar/proceso/999",
            status_raw="Publicada",
        )

        items = connector._filter_records([comprar_row, contratar_row, unrelated_row])
        self.assertEqual([item.external_id for item in items], ["105-0001-LPU26", "76/2026"])

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

    def test_pbac_source_url_uses_expanded_listing(self) -> None:
        html = """
        <table id="ctl00_CPH1_CtrlTablasPortal_gridPliegoAperturaProxima">
          <tr>
            <th>Número de Proceso</th><th>Nombre de Proceso</th><th>Tipo de Proceso</th><th>Fecha de Apertura</th><th>Estado</th><th>Unidad Ejecutora</th>
          </tr>
          <tr>
            <td><a href="javascript:__doPostBack('ctl00$CPH1$CtrlTablasPortal$gridPliegoAperturaProxima$ctl02$lnkNumeroProceso','')">2026-29-2-350</a></td>
            <td>Servicio de instalación y puesta en funcionamiento de una Red de Área Local</td>
            <td><p>Licitación Privada</p></td>
            <td>13/04/2026 08:00 Hrs.</td>
            <td><p>Publicado</p></td>
            <td><p>103.14.12.1 - Hospital Dr. I. Iriarte - Quilmes</p></td>
          </tr>
        </table>
        """
        connector = PbacConnector()
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table", id=connector.table_id)
        self.assertIsNotNone(table)
        self.assertEqual(connector.listing_url, "https://pbac.cgp.gba.gov.ar/ListarAperturaProxima.aspx")

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

    def test_gcba_extract_rows(self) -> None:
        html = """
        <table>
          <tr>
            <th>Número de Proceso</th><th>Nombre de Proceso</th><th>Tipo de Proceso</th><th>Fecha de Apertura</th><th>Estado</th><th>Unidad Ejecutora</th>
          </tr>
          <tr>
            <td><a href="/PLIEGO/VistaPreviaPliegoCiudadano.aspx?qs=abc123">414-0373-LPU26</a></td>
            <td>ADQUISICION DE REACTIVOS PARA MARCADORES TUMORALES Y HORMONAS-LABORATORIO CENTRAL</td>
            <td>Licitación Pública</td>
            <td>14/04/2026 08:00 Hrs.</td>
            <td>Publicado</td>
            <td>414 - HTAL. MARIA CURIE</td>
          </tr>
        </table>
        """
        items = GcbaConnector()._extract_rows(html)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].external_id, "414-0373-LPU26")
        self.assertEqual(items[0].procedure_type, "Licitación Pública")
        self.assertEqual(items[0].status_raw, "Publicado")
        self.assertEqual(items[0].organization, "414 - HTAL. MARIA CURIE")
        self.assertIn("/PLIEGO/VistaPreviaPliegoCiudadano.aspx?qs=abc123", items[0].source_url)

    def test_gcba_extract_detail_summary(self) -> None:
        html = """
        <html>
          <body>
            <table>
              <tr><td>Número del proceso de compra</td><td>434-0826-CME26</td></tr>
              <tr><td>Nombre del proceso de compra</td><td>Adquisición Cateter Guía y otros - Neurocirugía - LOPEZ PABLO</td></tr>
              <tr><td>Unidad Operativa de Adquisiciones</td><td>434 - HTAL.DONACION FRANCISCO SANTOJANNI</td></tr>
              <tr><td>Objeto de la contratación</td><td>Adquisición Cateter Guía y otros - Neurocirugía - LOPEZ PABLO</td></tr>
              <tr><td>Procedimiento de selección</td><td>Contratación menor</td></tr>
              <tr><td>Fecha y hora estimada de publicación en el portal</td><td>6/4/2026 15:00:00</td></tr>
              <tr><td>Fecha y hora acto de apertura</td><td>15/4/2026 12:30:00</td></tr>
              <tr><td>Monto</td><td>$ 13.300.000,00</td></tr>
            </table>
          </body>
        </html>
        """
        item = GcbaConnector().extract_detail_summary(
            html,
            "https://www.buenosairescompras.gob.ar/PLIEGO/VistaPreviaPliegoCiudadano.aspx?qs=abc123",
        )
        self.assertEqual(item.external_id, "434-0826-CME26")
        self.assertEqual(item.procedure_type, "Contratación menor")
        self.assertEqual(item.organization, "434 - HTAL.DONACION FRANCISCO SANTOJANNI")
        self.assertEqual(str(item.estimated_amount), "13300000.00")
        self.assertIn("PLIEGO/VistaPreviaPliegoCiudadano.aspx", item.source_url)

    def test_gcba_extract_total_results(self) -> None:
        html = """
        <h4><small>
          <span id="ctl00_CPH1_lblCantidadListaPliegos">Se han encontrado (203) resultados para su búsqueda.</span>
        </small></h4>
        """
        self.assertEqual(GcbaConnector()._extract_total_results(html), 203)

    def test_gcba_extract_records_from_staged_json_payload(self) -> None:
        payload = {
            "source": "licitaciones-caba",
            "records": [
                {
                    "external_id": "434-0826-CME26",
                    "title": "Adquisición Cateter Guía y otros - Neurocirugía - LOPEZ PABLO",
                    "description_raw": "Objeto de la contratación",
                    "organization": "434 - HTAL.DONACION FRANCISCO SANTOJANNI",
                    "jurisdiction": "Ciudad Autónoma de Buenos Aires",
                    "procedure_type": "Contratación menor",
                    "publication_date": "2026-04-06",
                    "deadline_date": "2026-04-15T12:30:00+00:00",
                    "opening_date": "2026-04-15T12:30:00+00:00",
                    "estimated_amount": "13300000.00",
                    "currency": "ARS",
                    "source_url": "https://www.buenosairescompras.gob.ar/PLIEGO/VistaPreviaPliegoCiudadano.aspx?qs=abc123",
                    "status_raw": "Publicado",
                }
            ],
        }
        items = GcbaConnector()._extract_records_from_json_payload(payload)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].external_id, "434-0826-CME26")
        self.assertEqual(items[0].organization, "434 - HTAL.DONACION FRANCISCO SANTOJANNI")
        self.assertEqual(str(items[0].estimated_amount), "13300000.00")
        self.assertEqual(items[0].publication_date.isoformat(), "2026-04-06")

    def test_entre_rios_extract_rows(self) -> None:
        html = """
        <table id="tabla-resultados">
          <thead>
            <tr>
              <td>PROCEDIMIENTO DE CONTRATACIÓN</td>
              <td>OBJETO</td>
              <td>DESTINO</td>
              <td>ORGANISMO</td>
            </tr>
          </thead>
          <tbody>
            <tr class="table-primary">
              <td><strong>Solicitud De Cotización 24/2025</strong></td>
              <td>ADQUISICIÓN DE AIRE ACONDICIONADOS</td>
              <td>DIRECCIÓN PROVINCIAL DE VIALIDAD</td>
              <td>Dirección Provincial de Vialidad</td>
            </tr>
          </tbody>
        </table>
        """
        items = EntreRiosConnector()._extract_rows(html)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].external_id, "24/2025")
        self.assertEqual(items[0].procedure_type, "Solicitud De Cotización")
        self.assertEqual(items[0].organization, "Dirección Provincial de Vialidad")
        self.assertIn("Destino: DIRECCIÓN PROVINCIAL DE VIALIDAD", items[0].description_raw or "")
        self.assertEqual(items[0].status_raw, "En proceso de evaluación")

    def test_san_juan_extract_records(self) -> None:
        html = """
        <script>
        var obj={"licitaciones":{"res":[
          {
            "ID_PUBLICACION":7199,
            "F_PUBLICACION":"\\/Date(1776095717000)\\/",
            "ESTADOS":"Proceso de Apertura",
            "F_APERTURA":"\\/Date(1777258800000)\\/",
            "TIPO":"LICITACION PUBLICA",
            "INSTITUCION":"Secretaría de Seguridad y Orden Público",
            "OBJETO":"ADQUISICION DE CUBIERTAS VARIAS MEDIDAS",
            "PRESUPUESTO":301590400,
            "N_PUB":"04\\/2026",
            "EXPEDIENTE":"1601-000402-2026-EXP-GC",
            "INFORMACION":"Sala de licitaciones",
            "DOMI_APERTURA":"Av. Libertador 750 Oeste",
            "MAIL":"admin.policia@sanjuan.gov.ar",
            "H_APERTURA":"09:30 AM",
            "FPRESENTACION":"\\/Date(1777258800000)\\/",
            "H_PRESENTACION":"08:30 AM"
          }
        ]}};
        </script>
        """
        items = SanJuanConnector()._extract_records(html)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].external_id, "04/2026")
        self.assertEqual(items[0].procedure_type, "LICITACION PUBLICA")
        self.assertEqual(items[0].organization, "Secretaría de Seguridad y Orden Público")
        self.assertEqual(str(items[0].estimated_amount), "301590400")
        self.assertIn("/index.php/detalle?id=7199", items[0].source_url)

    def test_la_rioja_extract_rows(self) -> None:
        html = """
        <table id="resultado" class="formulario">
          <tr>
            <th>Organismo</th><th>Objeto Contratacion</th><th>Procedimiento</th><th>Modalidad</th><th>Fecha Caducidad</th><th>Cuenta Regresiva</th><th></th>
          </tr>
          <tr>
            <td>Transporte, Transito y Seguridad Vial</td>
            <td>S/ADQUISICION DE RTOS. P/BICICLETAS</td>
            <td><img src="img/proced_cont_dir.gif"></td>
            <td><img src="img/modal_tram_sim.gif"></td>
            <td>14.04.2026 12:30</td>
            <td>1 dias</td>
            <td><a href="prov_aviso_anexo4_detalle.php?xxx2=86486">ver</a></td>
          </tr>
        </table>
        """
        items = LaRiojaConnector()._extract_rows(html)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].external_id, "86486")
        self.assertEqual(items[0].procedure_type, "Contratación Directa")
        self.assertEqual(items[0].organization, "Transporte, Transito y Seguridad Vial")
        self.assertIn("Trámite Simplificado", items[0].description_raw or "")
        self.assertIn("xxx2=86486", items[0].source_url)

    def test_tierra_del_fuego_extract_rows(self) -> None:
        html = """
        <article>
          <div class="mk-blog-meta">
            <h3 class="the-title"><a href="https://compras.tierradelfuego.gob.ar/?p=267766">LLAMADO A LICITACIÓN PUBLICA N° 01/2026 – EXPEDIENTE ELECTRONICO N° 423/2026</a></h3>
            <div class="mk-blog-meta-wrapper"><time datetime="2026-03-20"></time></div>
            <div class="the-excerpt"><p>OBJETO: adquisición de gas cloro envasado.</p></div>
          </div>
        </article>
        <article>
          <div class="mk-blog-meta">
            <h3 class="the-title"><a href="https://compras.tierradelfuego.gob.ar/?p=269516">ADJUDICACION - LICITACIÓN PÚBLICA N° 20-2025</a></h3>
            <div class="mk-blog-meta-wrapper"><time datetime="2026-04-09"></time></div>
            <div class="the-excerpt"><p>Comunicado de adjudicación.</p></div>
          </div>
        </article>
        """
        items = TierraDelFuegoConnector()._extract_rows(html)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].external_id, "01/2026")
        self.assertEqual(items[0].procedure_type, "Licitación Pública")
        self.assertEqual(items[0].publication_date.isoformat(), "2026-03-20")

    def test_neuquen_extract_rows(self) -> None:
        html = """
        <div class="page-content">
          <article class="post">
            <h2 class="entry-title"><a href="https://salud.neuquen.gob.ar/objeto-adquisicion-de-insumos-de-odontologia/">OBJETO: adquisición de INSUMOS DE ODONTOLOGÍA.</a></h2>
            <p>Licitación Pública Nº571 EX-2025-02421562-NEU-DESP#MS DECTO-2026-260-E-NEU-GPN IMPORTE ESTIMADO: $ 876.102.500,00 Destino: Distintos Servicios Asistenciales Fecha – hora y lugar de apertura: 9 de abril de 2026 – Hora: 10,00 Ministerio de Salud.</p>
          </article>
        </div>
        """
        items = NeuquenConnector()._extract_rows(html)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].external_id, "EX-2025-02421562-NEU-DESP#MS")
        self.assertEqual(items[0].organization, "Ministerio de Salud de la Provincia del Neuquén")
        self.assertEqual(str(items[0].estimated_amount), "876102500.00")
        self.assertEqual(items[0].opening_date.strftime("%Y-%m-%d %H:%M"), "2026-04-09 10:00")

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
