from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.tender import Source, Tender
from app.services.company_profiles import ensure_demo_company_profile
from app.services.source_access import replace_company_source_scope
from app.services.source_catalog import seed_source_catalog
from app.services.users import ensure_demo_company_admin_user, ensure_demo_user, ensure_platform_admin_user


def seed_demo_data(db: Session) -> None:
    profile = ensure_demo_company_profile(db)
    ensure_platform_admin_user(db)
    ensure_demo_company_admin_user(db)
    demo_user = ensure_demo_user(db)
    if demo_user.alert_preferences_json is None:
        demo_user.alert_preferences_json = {
            "min_score": 60,
            "channels": ["dashboard"],
            "receive_relevant": True,
            "receive_deadlines": True,
        }

    seed_source_catalog(db)
    db.flush()

    source = db.query(Source).filter_by(slug='comprar').one()
    pbac = db.query(Source).filter_by(slug='pbac').one()
    boletin = db.query(Source).filter_by(slug='boletin-oficial').one()
    replace_company_source_scope(db, profile=profile, source_scope_mode='custom', source_ids=[source.id, pbac.id, boletin.id])

    existing = db.query(Tender).count()
    if existing > 0:
        db.commit()
        return

    base_items = [
        Tender(
            source_id=source.id,
            external_id="demo-001",
            title="Adquisición de licencias y soporte de software de gestión documental",
            description_raw="Licitación demo para adquisición de licencias, soporte y servicios asociados.",
            organization="Ministerio de Salud",
            jurisdiction="Nación",
            procedure_type="Licitación Pública",
            publication_date=datetime(2026, 3, 20, tzinfo=UTC).date(),
            deadline_date=datetime(2026, 4, 10, 13, 0, tzinfo=UTC),
            opening_date=datetime(2026, 4, 10, 13, 30, tzinfo=UTC),
            estimated_amount=Decimal("25000000.00"),
            currency="ARS",
            source_url="https://comprar.gob.ar/demo/001",
            dedupe_hash="demo-hash-001",
            status_raw="Abierta",
        ),
        Tender(
            source_id=source.id,
            external_id="demo-002",
            title="Servicio de mantenimiento y mesa de ayuda para infraestructura IT",
            description_raw="Contratación de soporte de infraestructura, monitoreo y mesa de ayuda.",
            organization="ANSES",
            jurisdiction="Nación",
            procedure_type="Licitación Pública",
            publication_date=datetime(2026, 3, 25, tzinfo=UTC).date(),
            deadline_date=datetime(2026, 4, 8, 15, 0, tzinfo=UTC),
            opening_date=datetime(2026, 4, 8, 15, 30, tzinfo=UTC),
            estimated_amount=Decimal("18000000.00"),
            currency="ARS",
            source_url="https://comprar.gob.ar/demo/002",
            dedupe_hash="demo-hash-002",
            status_raw="Abierta",
        ),
    ]

    db.add_all(base_items)
    db.commit()
