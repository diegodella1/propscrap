from __future__ import annotations

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Response
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.config import get_settings
from app.errors import AuthenticationError, ConflictError, NotFoundError, ValidationError
from app.jobs.dispatch_alerts import run_alert_dispatch
from app.schemas.auth import AuthResponse, CompanyLookupRead, LoginRequest, MeUpdateRequest, SignupRequest
from app.jobs.generate_alerts import run_alert_generation
from app.jobs.enrich_tender import enrich_pending_tenders, enrich_tender
from app.jobs.ingest_source import ingest_source
from app.jobs.match_tenders import match_all_tenders, match_tender
from app.jobs.process_tender import process_tender
from app.models.admin_audit import AdminAuditEvent
from app.models.tender import Alert, CompanyProfile, Source, SourceRun, User
from app.schemas.admin import (
    AdminAlertRead,
    AdminAuditEventRead,
    AutomationSettingsRead,
    AutomationSettingsUpdateRequest,
    CompanyProfileAdminRead,
    CompanyProfileUpdateRequest,
    PublicPlatformSettingsRead,
    SourceAccessRead,
    SourceAccessUpdateRequest,
    SourceAdminRead,
    SourceCreateRequest,
    SourceUpdateRequest,
    UserRead,
    UserUpdateRequest,
    WhatsappOutboxMessageRead,
)
from app.schemas.tender import (
    SourceRead,
    SourceRunRead,
    TenderDetailRead,
    TenderListResponse,
    TenderRead,
)
from app.services.audit import record_admin_audit
from app.services.automation import run_automation_cycle
from app.services.alerts import list_recent_alerts
from app.services.auth import authenticate_user, create_session_token, create_user_account, read_session_user_id
from app.services.company_profiles import (
    ensure_demo_company_profile,
    get_company_profile,
    get_company_profile_for_user,
    update_company_profile,
)
from app.services.company_registry import lookup_company_by_cuit
from app.services.llm_enrichment import DEFAULT_MASTER_PROMPT
from app.services.source_access import (
    list_effective_source_ids_for_profile,
    list_selected_source_ids,
    list_source_rows,
    replace_company_source_scope,
)
from app.services.source_catalog import seed_source_catalog
from app.services.rate_limit import enforce_auth_rate_limit
from app.services.runtime_settings import get_automation_settings, update_automation_settings
from app.services.source_registry import ALLOWED_CONNECTOR_SLUGS
from app.services.tenders import get_tender_detail, list_saved_tenders, list_tenders
from app.services.users import ensure_demo_user, update_user
from app.services.whatsapp import read_whatsapp_outbox
from app.services.workflow import upsert_tender_state

router = APIRouter(prefix="/api/v1")
settings = get_settings()


class TenderStateUpdateRequest(BaseModel):
    state: str
    notes: str | None = None
    user_id: int | None = None
    alert_overrides_json: dict | None = None


def get_current_user(
    db: Session = Depends(get_db),
    session_token: str | None = Cookie(default=None, alias=settings.session_cookie_name),
) -> User:
    user_id = read_session_user_id(session_token)
    if user_id is None:
        raise AuthenticationError("Session not found")

    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None or not user.is_active:
        raise AuthenticationError("Session not found")
    return user


def require_company_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in {"admin", "manager"}:
        raise AuthenticationError("Admin access required")
    return current_user


def require_platform_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise AuthenticationError("Platform admin access required")
    return current_user


@router.post("/auth/signup", response_model=AuthResponse)
def signup(
    payload: SignupRequest,
    response: Response,
    db: Session = Depends(get_db),
    __: None = Depends(enforce_auth_rate_limit),
) -> AuthResponse:
    user = create_user_account(
        db,
        full_name=payload.full_name,
        email=payload.email,
        password=payload.password,
        cuit=payload.cuit,
        company_name=payload.company_name,
    )
    db.commit()
    db.refresh(user)
    _set_session_cookie(response, user)
    return AuthResponse(user=UserRead.model_validate(user))


@router.post("/auth/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
    __: None = Depends(enforce_auth_rate_limit),
) -> AuthResponse:
    user = authenticate_user(db, email=payload.email, password=payload.password)
    _set_session_cookie(response, user)
    return AuthResponse(user=UserRead.model_validate(user))


@router.post("/auth/logout")
def logout(response: Response) -> dict:
    response.delete_cookie(settings.session_cookie_name, path="/", samesite="lax")
    return {"status": "ok"}


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)


@router.patch("/me", response_model=UserRead)
def patch_me(
    payload: MeUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    final_whatsapp_number = payload.whatsapp_number if payload.whatsapp_number is not None else current_user.whatsapp_number
    final_whatsapp_opt_in = payload.whatsapp_opt_in if payload.whatsapp_opt_in is not None else current_user.whatsapp_opt_in
    final_telegram_chat_id = payload.telegram_chat_id if payload.telegram_chat_id is not None else current_user.telegram_chat_id
    final_telegram_opt_in = payload.telegram_opt_in if payload.telegram_opt_in is not None else current_user.telegram_opt_in
    user = update_user(
        db,
        current_user,
        full_name=payload.full_name,
        company_name=payload.company_name,
        cuit=payload.cuit,
        whatsapp_number=payload.whatsapp_number,
        whatsapp_opt_in=payload.whatsapp_opt_in,
        whatsapp_verified=bool(final_whatsapp_number and final_whatsapp_opt_in),
        telegram_chat_id=payload.telegram_chat_id,
        telegram_opt_in=payload.telegram_opt_in,
        telegram_verified=bool(final_telegram_chat_id and final_telegram_opt_in),
        alert_preferences_json=_build_me_alert_preferences(
            payload.alert_priority,
            payload.receive_relevant,
            payload.receive_deadlines,
            payload.whatsapp_opt_in,
            payload.email_opt_in,
            payload.telegram_opt_in_alerts,
            current_user.alert_preferences_json,
        ),
    )
    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)


@router.get("/company-lookup/cuit/{cuit}", response_model=CompanyLookupRead)
def get_company_lookup(cuit: str) -> CompanyLookupRead:
    result = lookup_company_by_cuit(cuit)
    return CompanyLookupRead.model_validate(
        {
            "cuit": result.cuit,
            "company_name": result.company_name,
            "legal_name": result.legal_name,
            "tax_status_json": result.tax_status_json,
            "company_data_source": result.company_data_source,
            "company_data_updated_at": result.company_data_updated_at,
            "jurisdictions": result.jurisdictions,
            "sectors": result.sectors,
        }
    )


@router.get("/me/company-profile", response_model=CompanyProfileAdminRead)
def get_my_company_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CompanyProfileAdminRead:
    profile = get_company_profile_for_user(db, current_user)
    db.commit()
    db.refresh(profile)
    return _serialize_company_profile(profile)


@router.post("/me/company-profile/rematch")
def rematch_my_company_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    profile = get_company_profile_for_user(db, current_user)
    result = match_all_tenders(db, profile_id=profile.id)
    db.commit()
    return {
        "status": "ok",
        "profile_id": profile.id,
        "matched_tenders": result["matched_tenders"],
        "profiles_processed": result["profiles_processed"],
    }


@router.put("/me/company-profile", response_model=CompanyProfileAdminRead)
def put_my_company_profile(
    payload: CompanyProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CompanyProfileAdminRead:
    profile = get_company_profile_for_user(db, current_user)
    profile = update_company_profile(
        db,
        profile,
        cuit=current_user.cuit,
        company_name=payload.company_name,
        legal_name=payload.legal_name,
        company_description=payload.company_description,
        sectors=payload.sectors,
        include_keywords=payload.include_keywords,
        exclude_keywords=payload.exclude_keywords,
        jurisdictions=payload.jurisdictions,
        preferred_buyers=payload.preferred_buyers,
        min_amount=payload.min_amount,
        max_amount=payload.max_amount,
        alert_preferences_json=payload.alert_preferences_json,
        tax_status_json=payload.tax_status_json,
    )
    current_user.company_name = profile.company_name
    db.add(current_user)
    db.commit()
    db.refresh(profile)
    return _serialize_company_profile(profile)


@router.get("/tenders", response_model=TenderListResponse)
def get_tenders(
    source: str | None = Query(default=None),
    jurisdiction: str | None = Query(default=None),
    min_score: int | None = Query(default=None, ge=0, le=100),
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
    session_token: str | None = Cookie(default=None, alias=settings.session_cookie_name),
) -> TenderListResponse:
    allowed_source_ids: list[int] | None = None
    user_id = read_session_user_id(session_token)
    if user_id is not None:
        current_user = db.execute(select(User).where(User.id == user_id, User.is_active.is_(True))).scalar_one_or_none()
        if current_user is not None and current_user.company_profile_id is not None and current_user.company_profile is not None:
            allowed_source_ids = list_effective_source_ids_for_profile(db, current_user.company_profile)
    items, total = list_tenders(
        db,
        source_slug=source,
        jurisdiction=jurisdiction,
        min_score=min_score,
        limit=limit,
        allowed_source_ids=allowed_source_ids,
    )
    return TenderListResponse(items=[TenderRead.model_validate(item) for item in items], total=total)


@router.get("/tenders/{tender_id}", response_model=TenderDetailRead)
def get_tender(
    tender_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TenderDetailRead:
    allowed_source_ids = list_effective_source_ids_for_profile(db, current_user.company_profile) if current_user.company_profile else None
    item = get_tender_detail(db, tender_id, allowed_source_ids=allowed_source_ids)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Tender not found: {tender_id}")
    return TenderDetailRead.model_validate(item)


@router.get("/saved-tenders", response_model=TenderListResponse)
def get_saved_tenders(
    limit: int = Query(default=100, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TenderListResponse:
    allowed_source_ids = list_effective_source_ids_for_profile(db, current_user.company_profile) if current_user.company_profile else None
    items, total = list_saved_tenders(db, user_id=current_user.id, limit=limit, allowed_source_ids=allowed_source_ids)
    return TenderListResponse(items=[TenderRead.model_validate(item) for item in items], total=total)


@router.get("/sources", response_model=list[SourceRead])
def get_sources(db: Session = Depends(get_db)) -> list[SourceRead]:
    seed_source_catalog(db)
    db.commit()
    rows = db.execute(select(Source).where(Source.is_active.is_(True)).order_by(Source.name.asc())).scalars().all()
    return [SourceRead.model_validate(row) for row in rows]


@router.get("/admin/sources", response_model=list[SourceAdminRead])
def get_admin_sources(
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
) -> list[SourceAdminRead]:
    seed_source_catalog(db)
    db.commit()
    rows = db.execute(select(Source).order_by(Source.created_at.desc(), Source.id.desc())).scalars().all()
    return [_serialize_source(row) for row in rows]


@router.post("/admin/sources", response_model=SourceAdminRead)
def create_source(
    payload: SourceCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
) -> SourceAdminRead:
    slug = payload.slug
    existing = db.execute(select(Source).where(Source.slug == slug)).scalar_one_or_none()
    if existing is not None:
        raise ConflictError(f"Source already exists: {slug}")

    source = Source(
        name=payload.name,
        slug=slug,
        source_type=payload.source_type,
        scraping_mode=payload.scraping_mode,
        connector_slug=payload.connector_slug,
        base_url=payload.base_url,
        config_json=payload.config_json,
        is_active=payload.is_active,
    )
    db.add(source)
    db.flush()
    record_admin_audit(
        db,
        actor_user_id=current_user.id,
        action="admin.source.create",
        detail={"source_id": source.id, "slug": source.slug},
    )
    db.commit()
    db.refresh(source)
    return _serialize_source(source)


@router.patch("/admin/sources/{source_id}", response_model=SourceAdminRead)
def update_source(
    source_id: int,
    payload: SourceUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
) -> SourceAdminRead:
    source = db.execute(select(Source).where(Source.id == source_id)).scalar_one_or_none()
    if source is None:
        raise NotFoundError(f"Source not found: {source_id}")

    if payload.name is not None:
        source.name = payload.name
    if payload.slug is not None:
        slug = payload.slug
        existing = db.execute(select(Source).where(Source.slug == slug, Source.id != source_id)).scalar_one_or_none()
        if existing is not None:
            raise ConflictError(f"Source already exists: {slug}")
        source.slug = slug
    if payload.source_type is not None:
        source.source_type = payload.source_type
    if payload.scraping_mode is not None:
        source.scraping_mode = payload.scraping_mode
    if payload.connector_slug is not None:
        source.connector_slug = payload.connector_slug
    if payload.base_url is not None:
        source.base_url = payload.base_url
    if payload.config_json is not None:
        source.config_json = payload.config_json
    if payload.is_active is not None:
        source.is_active = payload.is_active

    record_admin_audit(
        db,
        actor_user_id=current_user.id,
        action="admin.source.update",
        detail={"source_id": source_id, "slug": source.slug},
    )
    db.commit()
    db.refresh(source)
    return _serialize_source(source)


@router.get("/company-profiles")
def get_company_profiles(
    db: Session = Depends(get_db),
    _: User = Depends(require_company_admin),
) -> list[dict]:
    rows = db.execute(select(CompanyProfile).order_by(CompanyProfile.id.asc())).scalars().all()
    return [
        {
            "id": row.id,
            "company_name": row.company_name,
            "company_description": row.company_description,
            "jurisdictions": row.jurisdictions,
            "preferred_buyers": row.preferred_buyers,
        }
        for row in rows
    ]


@router.get("/admin/company-profiles", response_model=list[CompanyProfileAdminRead])
def get_admin_company_profiles(
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
) -> list[CompanyProfileAdminRead]:
    ensure_demo_company_profile(db)
    db.commit()
    rows = db.execute(select(CompanyProfile).order_by(CompanyProfile.id.asc())).scalars().all()
    return [_serialize_company_profile(row) for row in rows]


@router.put("/admin/company-profiles/{profile_id}", response_model=CompanyProfileAdminRead)
def put_company_profile(
    profile_id: int,
    payload: CompanyProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
) -> CompanyProfileAdminRead:
    profile = get_company_profile(db, profile_id)
    if profile is None:
        raise NotFoundError(f"Company profile not found: {profile_id}")

    profile = update_company_profile(
        db,
        profile,
        cuit=payload.cuit,
        company_name=payload.company_name,
        legal_name=payload.legal_name,
        company_description=payload.company_description,
        sectors=payload.sectors,
        include_keywords=payload.include_keywords,
        exclude_keywords=payload.exclude_keywords,
        jurisdictions=payload.jurisdictions,
        preferred_buyers=payload.preferred_buyers,
        min_amount=payload.min_amount,
        max_amount=payload.max_amount,
        alert_preferences_json=payload.alert_preferences_json,
        tax_status_json=payload.tax_status_json,
    )
    record_admin_audit(
        db,
        actor_user_id=current_user.id,
        action="admin.company_profile.update",
        detail={"profile_id": profile_id},
    )
    db.commit()
    db.refresh(profile)
    return _serialize_company_profile(profile)


@router.get("/me/source-access", response_model=SourceAccessRead)
def get_my_source_access(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_admin),
) -> SourceAccessRead:
    profile = get_company_profile_for_user(db, current_user)
    seed_source_catalog(db)
    db.commit()
    return _serialize_source_access(db, profile)


@router.put("/me/source-access", response_model=SourceAccessRead)
def put_my_source_access(
    payload: SourceAccessUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_admin),
) -> SourceAccessRead:
    profile = get_company_profile_for_user(db, current_user)
    replace_company_source_scope(
        db,
        profile=profile,
        source_scope_mode=payload.source_scope_mode,
        source_ids=payload.source_ids,
    )
    record_admin_audit(
        db,
        actor_user_id=current_user.id,
        action="company.source_scope.update",
        detail={"profile_id": profile.id, "mode": payload.source_scope_mode, "source_ids": payload.source_ids},
    )
    db.commit()
    db.refresh(profile)
    return _serialize_source_access(db, profile)


@router.get("/admin/company-profiles/{profile_id}/source-access", response_model=SourceAccessRead)
def get_admin_company_source_access(
    profile_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
) -> SourceAccessRead:
    seed_source_catalog(db)
    db.commit()
    profile = get_company_profile(db, profile_id)
    if profile is None:
        raise NotFoundError(f"Company profile not found: {profile_id}")
    return _serialize_source_access(db, profile)


@router.put("/admin/company-profiles/{profile_id}/source-access", response_model=SourceAccessRead)
def put_admin_company_source_access(
    profile_id: int,
    payload: SourceAccessUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
) -> SourceAccessRead:
    profile = get_company_profile(db, profile_id)
    if profile is None:
        raise NotFoundError(f"Company profile not found: {profile_id}")
    replace_company_source_scope(
        db,
        profile=profile,
        source_scope_mode=payload.source_scope_mode,
        source_ids=payload.source_ids,
    )
    record_admin_audit(
        db,
        actor_user_id=current_user.id,
        action="admin.company_source_scope.update",
        detail={"profile_id": profile.id, "mode": payload.source_scope_mode, "source_ids": payload.source_ids},
    )
    db.commit()
    db.refresh(profile)
    return _serialize_source_access(db, profile)


@router.get("/users", response_model=list[UserRead])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_admin),
) -> list[UserRead]:
    ensure_demo_user(db)
    db.commit()
    query = select(User).order_by(User.id.asc())
    if current_user.role != "admin":
        query = query.where(User.company_profile_id == current_user.company_profile_id)
    rows = db.execute(query).scalars().all()
    return [UserRead.model_validate(row) for row in rows]


@router.patch("/admin/users/{user_id}", response_model=UserRead)
def patch_user(
    user_id: int,
    payload: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_admin),
) -> UserRead:
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise NotFoundError(f"User not found: {user_id}")
    if current_user.role != "admin" and user.company_profile_id != current_user.company_profile_id:
        raise NotFoundError(f"User not found: {user_id}")
    if current_user.role != "admin" and payload.role is not None and payload.role not in {"manager", "analyst"}:
        raise ValidationError("Company admins cannot assign platform roles")

    user = update_user(
        db,
        user,
        full_name=payload.full_name,
        company_name=payload.company_name,
        cuit=payload.cuit,
        role=payload.role,
        is_active=payload.is_active,
        whatsapp_number=payload.whatsapp_number,
        whatsapp_opt_in=payload.whatsapp_opt_in,
        whatsapp_verified=payload.whatsapp_verified,
        telegram_chat_id=payload.telegram_chat_id,
        telegram_opt_in=payload.telegram_opt_in,
        telegram_verified=payload.telegram_verified,
        alert_preferences_json=payload.alert_preferences_json,
    )
    record_admin_audit(
        db,
        actor_user_id=current_user.id,
        action="admin.user.update",
        detail={"target_user_id": user_id},
    )
    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)


@router.get("/source-runs", response_model=list[SourceRunRead])
def get_source_runs(
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
) -> list[SourceRunRead]:
    rows = db.execute(select(SourceRun).order_by(SourceRun.started_at.desc()).limit(50)).scalars().all()
    return [SourceRunRead.model_validate(row) for row in rows]


@router.get("/alerts", response_model=list[AdminAlertRead])
def get_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_admin),
) -> list[AdminAlertRead]:
    rows = list_recent_alerts(db, limit=200)
    if current_user.role != "admin":
        rows = [row for row in rows if row.user.company_profile_id == current_user.company_profile_id]
    return [AdminAlertRead.model_validate(row) for row in rows]


@router.get("/admin/automation", response_model=AutomationSettingsRead)
def get_admin_automation(
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
) -> AutomationSettingsRead:
    settings_row = get_automation_settings(db)
    db.commit()
    db.refresh(settings_row)
    return _serialize_automation_settings(settings_row)


@router.get("/public/platform-settings", response_model=PublicPlatformSettingsRead)
def get_public_platform_settings(
    db: Session = Depends(get_db),
) -> PublicPlatformSettingsRead:
    settings_row = get_automation_settings(db)
    db.commit()
    db.refresh(settings_row)
    return PublicPlatformSettingsRead.model_validate(
        {
            "contact_email": settings_row.contact_email,
            "contact_whatsapp_number": settings_row.contact_whatsapp_number,
            "contact_telegram_handle": settings_row.contact_telegram_handle,
            "demo_booking_url": settings_row.demo_booking_url,
        }
    )


@router.patch("/admin/automation", response_model=AutomationSettingsRead)
def patch_admin_automation(
    payload: AutomationSettingsUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
) -> AutomationSettingsRead:
    settings_row = get_automation_settings(db)
    settings_row = update_automation_settings(
        db,
        settings_row,
        is_enabled=payload.is_enabled,
        ingestion_interval_hours=payload.ingestion_interval_hours,
        openai_api_key=payload.openai_api_key,
        openai_model=payload.openai_model,
        llm_master_prompt=payload.llm_master_prompt,
        contact_email=payload.contact_email,
        contact_whatsapp_number=payload.contact_whatsapp_number,
        contact_telegram_handle=payload.contact_telegram_handle,
        demo_booking_url=payload.demo_booking_url,
        resend_api_key=payload.resend_api_key,
        resend_from_email=payload.resend_from_email,
        email_delivery_enabled=payload.email_delivery_enabled,
        whatsapp_enabled=payload.whatsapp_enabled,
        whatsapp_provider=payload.whatsapp_provider,
        whatsapp_meta_token=payload.whatsapp_meta_token,
        whatsapp_meta_phone_number_id=payload.whatsapp_meta_phone_number_id,
        whatsapp_api_version=payload.whatsapp_api_version,
        telegram_enabled=payload.telegram_enabled,
        telegram_bot_token=payload.telegram_bot_token,
    )
    record_admin_audit(
        db,
        actor_user_id=current_user.id,
        action="admin.automation.update",
        detail={"automation_settings_id": settings_row.id},
    )
    db.commit()
    db.refresh(settings_row)
    return _serialize_automation_settings(settings_row)


@router.post("/admin/automation/run")
def run_admin_automation(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
) -> dict:
    result = run_automation_cycle(db)
    record_admin_audit(
        db,
        actor_user_id=current_user.id,
        action="admin.automation.run",
        detail={},
    )
    db.commit()
    return result


@router.post("/jobs/ingest/{source_slug}")
def run_ingest(
    source_slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
) -> dict:
    result = ingest_source(db, source_slug)
    record_admin_audit(
        db,
        actor_user_id=current_user.id,
        action="job.ingest",
        detail={"source_slug": source_slug},
    )
    db.commit()
    return result


@router.post("/jobs/process/{tender_id}")
def run_process_tender(
    tender_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
) -> dict:
    result = process_tender(db, tender_id)
    record_admin_audit(
        db,
        actor_user_id=current_user.id,
        action="job.process_tender",
        detail={"tender_id": tender_id},
    )
    db.commit()
    return result


@router.post("/jobs/enrich/{tender_id}")
def run_enrich_tender(
    tender_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
) -> dict:
    result = enrich_tender(db, tender_id)
    record_admin_audit(
        db,
        actor_user_id=current_user.id,
        action="job.enrich_tender",
        detail={"tender_id": tender_id},
    )
    db.commit()
    return result


@router.post("/jobs/enrich-pending")
def run_enrich_pending_job(
    limit: int | None = Query(default=None, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
) -> dict:
    result = enrich_pending_tenders(db, limit=limit)
    record_admin_audit(
        db,
        actor_user_id=current_user.id,
        action="job.enrich_pending",
        detail={"limit": limit},
    )
    db.commit()
    return result


@router.post("/jobs/match/{tender_id}")
def run_match_tender(
    tender_id: int,
    profile_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
) -> dict:
    result = match_tender(db, tender_id, profile_id=profile_id)
    record_admin_audit(
        db,
        actor_user_id=current_user.id,
        action="job.match_tender",
        detail={"tender_id": tender_id, "profile_id": profile_id},
    )
    db.commit()
    return result


@router.post("/jobs/match-all")
def run_match_all(
    profile_id: int | None = Query(default=None),
    batch_size: int | None = Query(default=None, ge=10, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
) -> dict:
    result = match_all_tenders(db, profile_id=profile_id, batch_size=batch_size)
    record_admin_audit(
        db,
        actor_user_id=current_user.id,
        action="job.match_all",
        detail={"profile_id": profile_id, "batch_size": batch_size},
    )
    db.commit()
    return result


@router.post("/jobs/alerts/generate")
def generate_alerts_job(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
) -> dict:
    result = run_alert_generation(db)
    record_admin_audit(
        db,
        actor_user_id=current_user.id,
        action="job.alerts.generate",
        detail={},
    )
    db.commit()
    return result


@router.post("/jobs/alerts/dispatch")
def dispatch_alerts_job(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
) -> dict:
    result = run_alert_dispatch(db)
    record_admin_audit(
        db,
        actor_user_id=current_user.id,
        action="job.alerts.dispatch",
        detail={},
    )
    db.commit()
    return result


@router.get("/admin/alerts/outbox", response_model=list[WhatsappOutboxMessageRead])
def get_whatsapp_alert_outbox(
    limit: int = Query(default=50, ge=1, le=200),
    _: User = Depends(require_platform_admin),
) -> list[WhatsappOutboxMessageRead]:
    return [WhatsappOutboxMessageRead.model_validate(item) for item in read_whatsapp_outbox(limit=limit)]


@router.get("/admin/audit-events", response_model=list[AdminAuditEventRead])
def get_admin_audit_events(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
) -> list[AdminAuditEventRead]:
    rows = (
        db.execute(select(AdminAuditEvent).order_by(AdminAuditEvent.created_at.desc(), AdminAuditEvent.id.desc()).limit(limit))
        .scalars()
        .all()
    )
    return [AdminAuditEventRead.model_validate(row) for row in rows]


@router.post("/tenders/{tender_id}/state")
def update_tender_state(
    tender_id: int,
    payload: TenderStateUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    user = current_user
    if current_user.role == "admin" and payload.user_id and payload.user_id != user.id:
        row = db.execute(select(User).where(User.id == payload.user_id)).scalar_one_or_none()
        if row is not None:
            user = row
    state = upsert_tender_state(
        db,
        tender_id=tender_id,
        user_id=user.id,
        state=payload.state,
        notes=payload.notes,
        alert_overrides_json=payload.alert_overrides_json,
    )
    db.commit()
    return {
        "tender_id": tender_id,
        "state": state.state,
        "user_id": user.id,
        "alert_overrides_json": state.alert_overrides_json,
    }


def _set_session_cookie(response: Response, user: User) -> None:
    response.set_cookie(
        key=settings.session_cookie_name,
        value=create_session_token(user),
        max_age=settings.session_max_age_seconds,
        httponly=True,
        samesite="lax",
        secure=settings.env != "development",
        path="/",
    )


def _build_me_alert_preferences(
    alert_priority: str | None,
    receive_relevant: bool | None,
    receive_deadlines: bool | None,
    whatsapp_opt_in: bool | None,
    email_opt_in: bool | None,
    telegram_opt_in_alerts: bool | None,
    existing: dict | None,
) -> dict:
    priority_map = {
        "alta": 75,
        "media": 60,
        "todas": 0,
    }
    preferences = dict(existing or {})
    channels = ["dashboard"]
    wants_email = email_opt_in if email_opt_in is not None else "email" in (preferences.get("channels") or [])
    if wants_email:
        channels.append("email")
    wants_whatsapp = whatsapp_opt_in if whatsapp_opt_in is not None else "whatsapp" in (preferences.get("channels") or [])
    if wants_whatsapp:
        channels.append("whatsapp")
    wants_telegram = telegram_opt_in_alerts if telegram_opt_in_alerts is not None else "telegram" in (preferences.get("channels") or [])
    if wants_telegram:
        channels.append("telegram")
    if alert_priority is not None:
        normalized_priority = alert_priority.strip().lower()
        if normalized_priority not in priority_map:
            raise ValidationError(f"Unknown alert priority: {alert_priority}")
        preferences["min_score"] = priority_map[normalized_priority]
    preferences["channels"] = channels
    if receive_relevant is not None:
        preferences["receive_relevant"] = receive_relevant
    if receive_deadlines is not None:
        preferences["receive_deadlines"] = receive_deadlines
    return preferences


def _serialize_company_profile(profile: CompanyProfile) -> CompanyProfileAdminRead:
    return CompanyProfileAdminRead.model_validate(
        {
            "id": profile.id,
            "cuit": profile.cuit,
            "company_name": profile.company_name,
            "legal_name": profile.legal_name,
            "company_description": profile.company_description,
            "sectors": profile.sectors,
            "include_keywords": profile.include_keywords,
            "exclude_keywords": profile.exclude_keywords,
            "jurisdictions": profile.jurisdictions,
            "preferred_buyers": profile.preferred_buyers,
            "min_amount": str(profile.min_amount) if profile.min_amount is not None else None,
            "max_amount": str(profile.max_amount) if profile.max_amount is not None else None,
            "alert_preferences_json": profile.alert_preferences_json,
            "tax_status_json": profile.tax_status_json,
            "company_data_source": profile.company_data_source,
            "company_data_updated_at": profile.company_data_updated_at,
            "source_scope_mode": profile.source_scope_mode,
        }
    )


def _serialize_source(source: Source) -> SourceAdminRead:
    return SourceAdminRead.model_validate(
        {
            "id": source.id,
            "name": source.name,
            "slug": source.slug,
            "source_type": source.source_type,
            "scraping_mode": source.scraping_mode,
            "connector_slug": source.connector_slug,
            "base_url": source.base_url,
            "config_json": source.config_json,
            "is_active": source.is_active,
            "last_run_at": source.last_run_at,
            "connector_available": (source.connector_slug or source.slug) in ALLOWED_CONNECTOR_SLUGS,
        }
    )


def _serialize_source_access(db: Session, profile: CompanyProfile) -> SourceAccessRead:
    rows = list_source_rows(db)
    selected_source_ids = list_selected_source_ids(db, profile)
    effective_source_ids = list_effective_source_ids_for_profile(db, profile)
    return SourceAccessRead.model_validate(
        {
            "profile_id": profile.id,
            "company_name": profile.company_name,
            "source_scope_mode": profile.source_scope_mode,
            "selected_source_ids": selected_source_ids,
            "effective_source_ids": effective_source_ids,
            "sources": [_serialize_source(row) for row in rows],
        }
    )


def _serialize_automation_settings(settings_row) -> AutomationSettingsRead:
    active_model = settings_row.openai_model_override or settings.openai_model
    active_prompt = settings_row.llm_master_prompt or DEFAULT_MASTER_PROMPT
    whatsapp_enabled = (
        settings_row.whatsapp_enabled_override
        if settings_row.whatsapp_enabled_override is not None
        else settings.whatsapp_enabled
    )
    whatsapp_provider = settings_row.whatsapp_provider_override or settings.whatsapp_provider
    whatsapp_api_version = settings_row.whatsapp_meta_api_version_override or settings.whatsapp_meta_api_version
    whatsapp_phone_number_id = (
        settings_row.whatsapp_meta_phone_number_id_override or settings.whatsapp_meta_phone_number_id
    )
    telegram_enabled = (
        settings_row.telegram_enabled_override
        if settings_row.telegram_enabled_override is not None
        else settings.telegram_enabled
    )
    return AutomationSettingsRead.model_validate(
        {
            "id": settings_row.id,
            "is_enabled": settings_row.is_enabled,
            "ingestion_interval_hours": settings_row.ingestion_interval_hours,
            "openai_api_key_configured": bool(settings_row.openai_api_key_override or settings.openai_api_key),
            "resend_api_key_configured": bool(settings_row.resend_api_key_override or settings.resend_api_key),
            "email_delivery_enabled": settings_row.email_delivery_enabled,
            "whatsapp_enabled": bool(whatsapp_enabled),
            "whatsapp_provider": whatsapp_provider,
            "whatsapp_api_version": whatsapp_api_version,
            "whatsapp_meta_token_configured": bool(settings_row.whatsapp_meta_token_override or settings.whatsapp_meta_token),
            "whatsapp_meta_phone_number_id": whatsapp_phone_number_id,
            "telegram_enabled": bool(telegram_enabled),
            "telegram_bot_token_configured": bool(settings_row.telegram_bot_token_override or settings.telegram_bot_token),
            "openai_model": active_model,
            "llm_master_prompt": active_prompt,
            "contact_email": settings_row.contact_email,
            "contact_whatsapp_number": settings_row.contact_whatsapp_number,
            "contact_telegram_handle": settings_row.contact_telegram_handle,
            "demo_booking_url": settings_row.demo_booking_url,
            "resend_from_email": settings_row.resend_from_email,
            "last_run_started_at": settings_row.last_run_started_at,
            "last_run_finished_at": settings_row.last_run_finished_at,
            "last_success_at": settings_row.last_success_at,
            "last_error_message": settings_row.last_error_message,
            "last_cycle_summary": settings_row.last_cycle_summary,
        }
    )
