from __future__ import annotations

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Response
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.config import get_settings
from app.errors import AuthenticationError, ConflictError, NotFoundError, ValidationError
from app.jobs.dispatch_alerts import run_alert_dispatch
from app.schemas.auth import AuthResponse, LoginRequest, MeUpdateRequest, SignupRequest
from app.jobs.generate_alerts import run_alert_generation
from app.jobs.enrich_tender import enrich_pending_tenders, enrich_tender
from app.jobs.ingest_source import ingest_source
from app.jobs.match_tenders import match_all_tenders, match_tender
from app.jobs.process_tender import process_tender
from app.models.tender import Alert, CompanyProfile, Source, SourceRun, User
from app.schemas.admin import (
    AdminAlertRead,
    AutomationSettingsRead,
    AutomationSettingsUpdateRequest,
    CompanyProfileAdminRead,
    CompanyProfileUpdateRequest,
    SourceAdminRead,
    SourceCreateRequest,
    SourceUpdateRequest,
    UserRead,
    UserUpdateRequest,
)
from app.schemas.tender import (
    SourceRead,
    SourceRunRead,
    TenderDetailRead,
    TenderListResponse,
    TenderRead,
)
from app.services.automation import run_automation_cycle
from app.services.alerts import list_recent_alerts
from app.services.auth import authenticate_user, create_session_token, create_user_account, read_session_user_id
from app.services.company_profiles import (
    ensure_demo_company_profile,
    get_company_profile,
    get_company_profile_for_user,
    update_company_profile,
)
from app.services.llm_enrichment import DEFAULT_MASTER_PROMPT
from app.services.runtime_settings import get_automation_settings, update_automation_settings
from app.services.source_registry import CONNECTORS
from app.services.tenders import get_tender_detail, list_tenders
from app.services.users import ensure_demo_user, update_user
from app.services.workflow import upsert_tender_state

router = APIRouter(prefix="/api/v1")
settings = get_settings()


class TenderStateUpdateRequest(BaseModel):
    state: str
    notes: str | None = None
    user_id: int | None = None


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
def signup(payload: SignupRequest, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
    user = create_user_account(
        db,
        full_name=payload.full_name,
        email=payload.email,
        password=payload.password,
        company_name=payload.company_name,
    )
    db.commit()
    db.refresh(user)
    _set_session_cookie(response, user)
    return AuthResponse(user=UserRead.model_validate(user))


@router.post("/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
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
    user = update_user(
        db,
        current_user,
        full_name=payload.full_name,
        company_name=payload.company_name,
        whatsapp_number=payload.whatsapp_number,
        whatsapp_opt_in=payload.whatsapp_opt_in,
        whatsapp_verified=bool(final_whatsapp_number and final_whatsapp_opt_in),
        alert_preferences_json=_build_me_alert_preferences(
            payload.alert_priority,
            payload.receive_relevant,
            payload.receive_deadlines,
            payload.whatsapp_opt_in,
            current_user.alert_preferences_json,
        ),
    )
    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)


@router.get("/me/company-profile", response_model=CompanyProfileAdminRead)
def get_my_company_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CompanyProfileAdminRead:
    profile = get_company_profile_for_user(db, current_user)
    db.commit()
    db.refresh(profile)
    return _serialize_company_profile(profile)


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
        company_name=payload.company_name,
        company_description=payload.company_description,
        sectors=payload.sectors,
        include_keywords=payload.include_keywords,
        exclude_keywords=payload.exclude_keywords,
        jurisdictions=payload.jurisdictions,
        preferred_buyers=payload.preferred_buyers,
        min_amount=payload.min_amount,
        max_amount=payload.max_amount,
        alert_preferences_json=payload.alert_preferences_json,
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
) -> TenderListResponse:
    items, total = list_tenders(
        db,
        source_slug=source,
        jurisdiction=jurisdiction,
        min_score=min_score,
        limit=limit,
    )
    return TenderListResponse(items=[TenderRead.model_validate(item) for item in items], total=total)


@router.get("/tenders/{tender_id}", response_model=TenderDetailRead)
def get_tender(tender_id: int, db: Session = Depends(get_db)) -> TenderDetailRead:
    item = get_tender_detail(db, tender_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Tender not found: {tender_id}")
    return TenderDetailRead.model_validate(item)


@router.get("/sources", response_model=list[SourceRead])
def get_sources(db: Session = Depends(get_db)) -> list[SourceRead]:
    rows = db.execute(select(Source).order_by(Source.name.asc())).scalars().all()
    return [SourceRead.model_validate(row) for row in rows]


@router.get("/admin/sources", response_model=list[SourceAdminRead])
def get_admin_sources(
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
) -> list[SourceAdminRead]:
    rows = db.execute(select(Source).order_by(Source.created_at.desc(), Source.id.desc())).scalars().all()
    return [
        SourceAdminRead.model_validate(
            {
                "id": row.id,
                "name": row.name,
                "slug": row.slug,
                "source_type": row.source_type,
                "base_url": row.base_url,
                "is_active": row.is_active,
                "last_run_at": row.last_run_at,
                "connector_available": row.slug in CONNECTORS,
            }
        )
        for row in rows
    ]


@router.post("/admin/sources", response_model=SourceAdminRead)
def create_source(
    payload: SourceCreateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
) -> SourceAdminRead:
    slug = payload.slug.strip().lower()
    existing = db.execute(select(Source).where(Source.slug == slug)).scalar_one_or_none()
    if existing is not None:
        raise ConflictError(f"Source already exists: {slug}")

    source = Source(
        name=payload.name.strip(),
        slug=slug,
        source_type=payload.source_type.strip(),
        base_url=payload.base_url.strip(),
        is_active=payload.is_active,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return SourceAdminRead.model_validate(
        {
            "id": source.id,
            "name": source.name,
            "slug": source.slug,
            "source_type": source.source_type,
            "base_url": source.base_url,
            "is_active": source.is_active,
            "last_run_at": source.last_run_at,
            "connector_available": source.slug in CONNECTORS,
        }
    )


@router.patch("/admin/sources/{source_id}", response_model=SourceAdminRead)
def update_source(
    source_id: int,
    payload: SourceUpdateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
) -> SourceAdminRead:
    source = db.execute(select(Source).where(Source.id == source_id)).scalar_one_or_none()
    if source is None:
        raise NotFoundError(f"Source not found: {source_id}")

    if payload.name is not None:
        source.name = payload.name.strip()
    if payload.slug is not None:
        slug = payload.slug.strip().lower()
        existing = db.execute(select(Source).where(Source.slug == slug, Source.id != source_id)).scalar_one_or_none()
        if existing is not None:
            raise ConflictError(f"Source already exists: {slug}")
        source.slug = slug
    if payload.source_type is not None:
        source.source_type = payload.source_type.strip()
    if payload.base_url is not None:
        source.base_url = payload.base_url.strip()
    if payload.is_active is not None:
        source.is_active = payload.is_active

    db.commit()
    db.refresh(source)
    return SourceAdminRead.model_validate(
        {
            "id": source.id,
            "name": source.name,
            "slug": source.slug,
            "source_type": source.source_type,
            "base_url": source.base_url,
            "is_active": source.is_active,
            "last_run_at": source.last_run_at,
            "connector_available": source.slug in CONNECTORS,
        }
    )


@router.get("/company-profiles")
def get_company_profiles(db: Session = Depends(get_db)) -> list[dict]:
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
    _: User = Depends(require_platform_admin),
) -> CompanyProfileAdminRead:
    profile = get_company_profile(db, profile_id)
    if profile is None:
        raise NotFoundError(f"Company profile not found: {profile_id}")

    profile = update_company_profile(
        db,
        profile,
        company_name=payload.company_name,
        company_description=payload.company_description,
        sectors=payload.sectors,
        include_keywords=payload.include_keywords,
        exclude_keywords=payload.exclude_keywords,
        jurisdictions=payload.jurisdictions,
        preferred_buyers=payload.preferred_buyers,
        min_amount=payload.min_amount,
        max_amount=payload.max_amount,
        alert_preferences_json=payload.alert_preferences_json,
    )
    db.commit()
    db.refresh(profile)
    return _serialize_company_profile(profile)


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
        role=payload.role,
        is_active=payload.is_active,
        whatsapp_number=payload.whatsapp_number,
        whatsapp_opt_in=payload.whatsapp_opt_in,
        whatsapp_verified=payload.whatsapp_verified,
        alert_preferences_json=payload.alert_preferences_json,
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


@router.patch("/admin/automation", response_model=AutomationSettingsRead)
def patch_admin_automation(
    payload: AutomationSettingsUpdateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
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
    )
    db.commit()
    db.refresh(settings_row)
    return _serialize_automation_settings(settings_row)


@router.post("/admin/automation/run")
def run_admin_automation(
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
) -> dict:
    return run_automation_cycle(db)


@router.post("/jobs/ingest/{source_slug}")
def run_ingest(
    source_slug: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
) -> dict:
    return ingest_source(db, source_slug)


@router.post("/jobs/process/{tender_id}")
def run_process_tender(
    tender_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
) -> dict:
    return process_tender(db, tender_id)


@router.post("/jobs/enrich/{tender_id}")
def run_enrich_tender(
    tender_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
) -> dict:
    return enrich_tender(db, tender_id)


@router.post("/jobs/enrich-pending")
def run_enrich_pending_job(
    limit: int | None = Query(default=None, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
) -> dict:
    return enrich_pending_tenders(db, limit=limit)


@router.post("/jobs/match/{tender_id}")
def run_match_tender(
    tender_id: int,
    profile_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
) -> dict:
    return match_tender(db, tender_id, profile_id=profile_id)


@router.post("/jobs/match-all")
def run_match_all(
    profile_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
) -> dict:
    return match_all_tenders(db, profile_id=profile_id)


@router.post("/jobs/alerts/generate")
def generate_alerts_job(
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
) -> dict:
    return run_alert_generation(db)


@router.post("/jobs/alerts/dispatch")
def dispatch_alerts_job(
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
) -> dict:
    return run_alert_dispatch(db)


@router.post("/tenders/{tender_id}/state")
def update_tender_state(
    tender_id: int,
    payload: TenderStateUpdateRequest,
    db: Session = Depends(get_db),
) -> dict:
    user = ensure_demo_user(db)
    if payload.user_id and payload.user_id != user.id:
        row = db.execute(select(User).where(User.id == payload.user_id)).scalar_one_or_none()
        if row:
            user = row
    state = upsert_tender_state(
        db,
        tender_id=tender_id,
        user_id=user.id,
        state=payload.state,
        notes=payload.notes,
    )
    db.commit()
    return {"tender_id": tender_id, "state": state.state, "user_id": user.id}


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
    existing: dict | None,
) -> dict:
    priority_map = {
        "alta": 75,
        "media": 60,
        "todas": 0,
    }
    preferences = dict(existing or {})
    channels = ["dashboard"]
    wants_whatsapp = whatsapp_opt_in if whatsapp_opt_in is not None else "whatsapp" in (preferences.get("channels") or [])
    if wants_whatsapp:
        channels.append("whatsapp")
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
            "company_name": profile.company_name,
            "company_description": profile.company_description,
            "sectors": profile.sectors,
            "include_keywords": profile.include_keywords,
            "exclude_keywords": profile.exclude_keywords,
            "jurisdictions": profile.jurisdictions,
            "preferred_buyers": profile.preferred_buyers,
            "min_amount": str(profile.min_amount) if profile.min_amount is not None else None,
            "max_amount": str(profile.max_amount) if profile.max_amount is not None else None,
            "alert_preferences_json": profile.alert_preferences_json,
        }
    )


def _serialize_automation_settings(settings_row) -> AutomationSettingsRead:
    active_model = settings_row.openai_model_override or settings.openai_model
    active_prompt = settings_row.llm_master_prompt or DEFAULT_MASTER_PROMPT
    return AutomationSettingsRead.model_validate(
        {
            "id": settings_row.id,
            "is_enabled": settings_row.is_enabled,
            "ingestion_interval_hours": settings_row.ingestion_interval_hours,
            "openai_api_key_configured": bool(settings_row.openai_api_key_override or settings.openai_api_key),
            "openai_model": active_model,
            "llm_master_prompt": active_prompt,
            "last_run_started_at": settings_row.last_run_started_at,
            "last_run_finished_at": settings_row.last_run_finished_at,
            "last_success_at": settings_row.last_success_at,
            "last_error_message": settings_row.last_error_message,
            "last_cycle_summary": settings_row.last_cycle_summary,
        }
    )
