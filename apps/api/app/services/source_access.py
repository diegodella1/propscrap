from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.errors import ValidationError
from app.models.tender import CompanyProfile, CompanyProfileSource, Source

SOURCE_SCOPE_MODES = {"all_active", "custom"}


def list_source_rows(db: Session) -> list[Source]:
    return db.execute(select(Source).order_by(Source.name.asc(), Source.id.asc())).scalars().all()


def list_selected_source_ids(db: Session, profile: CompanyProfile) -> list[int]:
    return list(
        db.execute(
            select(CompanyProfileSource.source_id)
            .where(CompanyProfileSource.company_profile_id == profile.id)
            .order_by(CompanyProfileSource.source_id.asc())
        ).scalars().all()
    )


def list_effective_source_ids_for_profile(db: Session, profile: CompanyProfile) -> list[int]:
    if profile.source_scope_mode == "custom":
        return list(
            db.execute(
                select(Source.id)
                .join(CompanyProfileSource, CompanyProfileSource.source_id == Source.id)
                .where(CompanyProfileSource.company_profile_id == profile.id, Source.is_active.is_(True))
                .order_by(Source.id.asc())
            ).scalars().all()
        )
    return list(
        db.execute(select(Source.id).where(Source.is_active.is_(True)).order_by(Source.id.asc())).scalars().all()
    )


def replace_company_source_scope(
    db: Session,
    *,
    profile: CompanyProfile,
    source_scope_mode: str,
    source_ids: list[int],
) -> CompanyProfile:
    if source_scope_mode not in SOURCE_SCOPE_MODES:
        raise ValidationError(f"Unknown source_scope_mode: {source_scope_mode}")

    normalized_ids = sorted({int(value) for value in source_ids})
    if normalized_ids:
        valid_ids = set(
            db.execute(select(Source.id).where(Source.id.in_(normalized_ids))).scalars().all()
        )
        missing_ids = [value for value in normalized_ids if value not in valid_ids]
        if missing_ids:
            raise ValidationError(f"Unknown source ids: {', '.join(str(value) for value in missing_ids)}")

    profile.source_scope_mode = source_scope_mode
    db.add(profile)
    db.execute(delete(CompanyProfileSource).where(CompanyProfileSource.company_profile_id == profile.id))
    if source_scope_mode == "custom":
        for source_id in normalized_ids:
            db.add(CompanyProfileSource(company_profile_id=profile.id, source_id=source_id))
    db.flush()
    return profile
