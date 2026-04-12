from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
import os
import sqlite3
import tempfile
import time
from typing import Iterator
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import httpx
from bs4 import BeautifulSoup

from app.config import get_settings
from app.errors import ConfigurationError, ExternalServiceError, ValidationError

PROJECT_ROOT = Path(__file__).resolve().parents[4]
CACHE_DIR = PROJECT_ROOT / "data" / "cache" / "company_registry"
PADRON_DB_PATH = CACHE_DIR / "arca_padron.sqlite3"
PADRON_LOCK_PATH = CACHE_DIR / "arca_padron.lock"


@dataclass(slots=True)
class CompanyLookupResult:
    cuit: str
    company_name: str
    legal_name: str
    tax_status_json: dict
    company_data_source: str
    company_data_updated_at: datetime
    jurisdictions: list[str] | None = None
    sectors: list[str] | None = None


def normalize_cuit(raw_value: str) -> str:
    digits = "".join(char for char in raw_value if char.isdigit())
    if len(digits) != 11:
        raise ValidationError("Ingresá un CUIT argentino válido de 11 dígitos")
    return digits


def validate_cuit(raw_value: str) -> str:
    cuit = normalize_cuit(raw_value)
    weights = (5, 4, 3, 2, 7, 6, 5, 4, 3, 2)
    total = sum(int(digit) * weight for digit, weight in zip(cuit[:10], weights, strict=True))
    remainder = 11 - (total % 11)
    verifier = 0 if remainder == 11 else 9 if remainder == 10 else remainder
    if verifier != int(cuit[-1]):
        raise ValidationError("El CUIT no es válido")
    return cuit


def lookup_company_by_cuit(cuit: str) -> CompanyLookupResult:
    normalized_cuit = validate_cuit(cuit)
    soap_result = _lookup_company_via_arca_ws(normalized_cuit)
    if soap_result is not None:
        return soap_result

    public_result = _lookup_company_via_public_padron(normalized_cuit)
    if public_result is None:
        raise NotFoundInRegistryError(f"No encontramos el CUIT {normalized_cuit} en ARCA")
    return public_result


class NotFoundInRegistryError(ValidationError):
    pass


def _lookup_company_via_arca_ws(cuit: str) -> CompanyLookupResult | None:
    settings = get_settings()
    if not (settings.arca_ws_token and settings.arca_ws_sign and settings.arca_ws_cuit_representada):
        return None

    envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:a5="http://a5.soap.ws.server.puc.sr/">
  <soapenv:Header/>
  <soapenv:Body>
    <a5:getPersona_v2>
      <token>{settings.arca_ws_token}</token>
      <sign>{settings.arca_ws_sign}</sign>
      <cuitRepresentada>{settings.arca_ws_cuit_representada}</cuitRepresentada>
      <idPersona>{cuit}</idPersona>
    </a5:getPersona_v2>
  </soapenv:Body>
</soapenv:Envelope>
"""

    try:
        response = httpx.post(
            settings.arca_ws_constancia_url,
            content=envelope.encode("utf-8"),
            headers={"Content-Type": "text/xml; charset=utf-8", "SOAPAction": ""},
            timeout=30,
        )
        response.raise_for_status()
        return _parse_arca_ws_response(cuit, response.text)
    except httpx.HTTPError as exc:
        raise ExternalServiceError(f"No se pudo consultar ARCA para el CUIT {cuit}") from exc
    except ValidationError:
        raise
    except Exception:
        return None


def _parse_arca_ws_response(cuit: str, xml_payload: str) -> CompanyLookupResult:
    try:
        root = ET.fromstring(xml_payload)
    except ET.ParseError as exc:
        raise ExternalServiceError("ARCA devolvió una respuesta inválida") from exc

    error_messages = [
        (node.text or "").strip()
        for node in root.iter()
        if _tag_suffix(node.tag) in {"errorConstancia", "errorMonotributo", "errorRegimenGeneral", "faultstring"}
        and (node.text or "").strip()
    ]
    if error_messages:
        raise ValidationError(error_messages[0])

    data_general = _first_descendant(root, "datosGenerales")
    if data_general is None:
        raise ValidationError(f"No encontramos datos oficiales para el CUIT {cuit}")

    legal_name = (
        _text_of(data_general, "razonSocial")
        or _text_of(data_general, "denominacion")
        or _join_non_empty([_text_of(data_general, "apellido"), _text_of(data_general, "nombre")], ", ")
        or _join_non_empty([_text_of(data_general, "nombre"), _text_of(data_general, "apellido")], " ")
    )
    if not legal_name:
        raise ValidationError(f"No encontramos denominación oficial para el CUIT {cuit}")

    province = _text_of(_first_descendant(data_general, "domicilioFiscal"), "descripcionProvincia")
    locality = _text_of(_first_descendant(data_general, "domicilioFiscal"), "localidad")

    activities: list[str] = []
    for activity in _all_descendants(root, "actividad"):
        description = _text_of(activity, "descripcionActividad") or _text_of(activity, "descripcion")
        if description and description not in activities:
            activities.append(description)

    tax_status = {
        "tipo_persona": _text_of(data_general, "tipoPersona"),
        "estado_clave": _text_of(data_general, "estadoClave"),
        "mes_cierre": _text_of(data_general, "mesCierre"),
        "localidad": locality,
        "provincia": province,
        "activities": activities,
    }

    jurisdictions = [province] if province else None
    sectors = activities[:5] or None
    now = datetime.now(tz=UTC)
    return CompanyLookupResult(
        cuit=cuit,
        company_name=legal_name,
        legal_name=legal_name,
        tax_status_json=tax_status,
        company_data_source="arca_ws_constancia_inscripcion",
        company_data_updated_at=now,
        jurisdictions=jurisdictions,
        sectors=sectors,
    )


def _lookup_company_via_public_padron(cuit: str) -> CompanyLookupResult | None:
    conn = _ensure_public_padron_db()
    try:
        row = conn.execute(
            """
            SELECT cuit, legal_name, ganancias_status, iva_status, monotributo_status,
                   integrante_sociedad, empleador, actividad_monotributo, synced_at
            FROM arca_padron
            WHERE cuit = ?
            """,
            (cuit,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None

    synced_at = datetime.fromisoformat(row["synced_at"])
    tax_status = {
        "ganancias": row["ganancias_status"],
        "iva": row["iva_status"],
        "monotributo": row["monotributo_status"],
        "integrante_sociedad": row["integrante_sociedad"] == "S",
        "empleador": row["empleador"] == "S",
        "actividad_monotributo": row["actividad_monotributo"],
    }
    return CompanyLookupResult(
        cuit=row["cuit"],
        company_name=row["legal_name"],
        legal_name=row["legal_name"],
        tax_status_json=tax_status,
        company_data_source="arca_padron_publico",
        company_data_updated_at=synced_at,
        sectors=None,
        jurisdictions=None,
    )


def _ensure_public_padron_db() -> sqlite3.Connection:
    settings = get_settings()
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if _padron_db_is_fresh(settings.arca_padron_cache_hours):
        return _open_padron_connection()

    with _exclusive_lock(PADRON_LOCK_PATH):
        if _padron_db_is_fresh(settings.arca_padron_cache_hours):
            return _open_padron_connection()
        _refresh_public_padron_index()
        return _open_padron_connection()


def _padron_db_is_fresh(max_age_hours: int) -> bool:
    if not PADRON_DB_PATH.exists():
        return False
    max_age = timedelta(hours=max_age_hours)
    modified_at = datetime.fromtimestamp(PADRON_DB_PATH.stat().st_mtime, tz=UTC)
    return datetime.now(tz=UTC) - modified_at <= max_age


def _open_padron_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(PADRON_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _refresh_public_padron_index() -> None:
    settings = get_settings()
    now = datetime.now(tz=UTC).isoformat()
    archive_url = _resolve_public_padron_archive_url(settings.arca_padron_archive_url)
    with httpx.stream("GET", archive_url, follow_redirects=True, timeout=120) as response:
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as archive_file:
            archive_path = Path(archive_file.name)
            for chunk in response.iter_bytes():
                archive_file.write(chunk)

    temp_db_path = PADRON_DB_PATH.with_suffix(".tmp.sqlite3")
    if temp_db_path.exists():
        temp_db_path.unlink()

    try:
        with ZipFile(archive_path) as archive:
            members = archive.namelist()
            if not members:
                raise ExternalServiceError("El archivo público de ARCA llegó vacío")
            with archive.open(members[0], "r") as raw_file:
                conn = sqlite3.connect(temp_db_path)
                try:
                    conn.execute("PRAGMA journal_mode = DELETE")
                    conn.execute("PRAGMA synchronous = OFF")
                    conn.execute(
                        """
                        CREATE TABLE arca_padron (
                            cuit TEXT PRIMARY KEY,
                            legal_name TEXT NOT NULL,
                            ganancias_status TEXT,
                            iva_status TEXT,
                            monotributo_status TEXT,
                            integrante_sociedad TEXT,
                            empleador TEXT,
                            actividad_monotributo TEXT,
                            synced_at TEXT NOT NULL
                        )
                        """
                    )
                    batch: list[tuple[str, str, str, str, str, str, str, str, str]] = []
                    for raw_line in raw_file:
                        line = raw_line.decode("latin-1", errors="ignore").rstrip("\r\n")
                        if not line.strip():
                            continue
                        batch.append(_parse_public_padron_line(line, now))
                        if len(batch) >= 5000:
                            conn.executemany(
                                """
                                INSERT INTO arca_padron (
                                    cuit, legal_name, ganancias_status, iva_status, monotributo_status,
                                    integrante_sociedad, empleador, actividad_monotributo, synced_at
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """,
                                batch,
                            )
                            batch.clear()
                    if batch:
                        conn.executemany(
                            """
                            INSERT INTO arca_padron (
                                cuit, legal_name, ganancias_status, iva_status, monotributo_status,
                                integrante_sociedad, empleador, actividad_monotributo, synced_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            batch,
                        )
                    conn.execute("CREATE INDEX idx_arca_padron_legal_name ON arca_padron(legal_name)")
                    conn.commit()
                finally:
                    conn.close()
        os.replace(temp_db_path, PADRON_DB_PATH)
    except httpx.HTTPError as exc:
        raise ExternalServiceError("No se pudo descargar el padrón público de ARCA") from exc
    finally:
        archive_path.unlink(missing_ok=True)
        temp_db_path.unlink(missing_ok=True)


def _resolve_public_padron_archive_url(configured_url: str) -> str:
    if _url_exists(configured_url):
        return configured_url

    page_url = "https://www.afip.gob.ar/genericos/cInscripcion/archivoCompleto.asp"
    try:
        response = httpx.get(page_url, follow_redirects=True, timeout=30)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise ExternalServiceError("No se pudo abrir la página oficial de descargas de ARCA") from exc

    soup = BeautifulSoup(response.text, "html.parser")
    for link in soup.find_all("a", href=True):
        text = " ".join(link.get_text(" ", strip=True).split()).lower()
        href = link["href"].strip()
        if "archivo condición tributaria con denominación" in text and href.endswith(".zip"):
            return href

    raise ExternalServiceError("No se encontró el archivo oficial de padrón público con denominación en ARCA")


def _url_exists(url: str) -> bool:
    try:
        response = httpx.head(url, follow_redirects=True, timeout=20)
        return response.status_code < 400
    except httpx.HTTPError:
        return False


def _parse_public_padron_line(line: str, synced_at: str) -> tuple[str, str, str, str, str, str, str, str, str]:
    if len(line) < 51:
        raise ExternalServiceError("El formato del padrón público de ARCA cambió y no se pudo procesar")
    cuit = line[0:11].strip()
    legal_name = line[11:41].strip()
    ganancias_status = line[41:43].strip() or None
    iva_status = line[43:45].strip() or None
    monotributo_status = line[45:47].strip() or None
    integrante_sociedad = line[47:48].strip() or None
    empleador = line[48:49].strip() or None
    actividad_monotributo = line[49:51].strip() or None
    return (
        cuit,
        legal_name,
        ganancias_status or "",
        iva_status or "",
        monotributo_status or "",
        integrante_sociedad or "",
        empleador or "",
        actividad_monotributo or "",
        synced_at,
    )


@contextmanager
def _exclusive_lock(lock_path: Path, timeout_seconds: int = 120) -> Iterator[None]:
    start = time.time()
    while True:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            if time.time() - start > timeout_seconds:
                raise ConfigurationError("El índice local del padrón ARCA quedó bloqueado")
            time.sleep(0.2)

    try:
        os.write(fd, str(os.getpid()).encode("utf-8"))
        yield
    finally:
        os.close(fd)
        lock_path.unlink(missing_ok=True)


def _tag_suffix(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _first_descendant(node: ET.Element, suffix: str) -> ET.Element | None:
    for child in node.iter():
        if _tag_suffix(child.tag) == suffix:
            return child
    return None


def _all_descendants(node: ET.Element, suffix: str) -> list[ET.Element]:
    return [child for child in node.iter() if _tag_suffix(child.tag) == suffix]


def _text_of(node: ET.Element | None, suffix: str) -> str | None:
    if node is None:
        return None
    for child in node.iter():
        if _tag_suffix(child.tag) == suffix:
            value = (child.text or "").strip()
            return value or None
    return None


def _join_non_empty(values: list[str | None], separator: str) -> str | None:
    items = [value.strip() for value in values if value and value.strip()]
    return separator.join(items) if items else None
