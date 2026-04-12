from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.tender import Alert, Tender, TenderDocument, TenderMatch, TenderState


def list_tenders(
    db: Session,
    source_slug: str | None = None,
    jurisdiction: str | None = None,
    min_score: int | None = None,
    limit: int = 50,
) -> tuple[list[Tender], int]:
    query = (
        select(Tender)
        .options(
            joinedload(Tender.source),
            selectinload(Tender.matches),
            selectinload(Tender.states),
            selectinload(Tender.alerts),
        )
        .order_by(Tender.publication_date.desc().nullslast(), Tender.id.desc())
    )
    count_query = select(func.count()).select_from(Tender)

    if source_slug:
        query = query.where(Tender.source.has(slug=source_slug))
        count_query = count_query.where(Tender.source.has(slug=source_slug))

    if jurisdiction:
        query = query.where(Tender.jurisdiction == jurisdiction)
        count_query = count_query.where(Tender.jurisdiction == jurisdiction)

    if min_score is not None:
        query = query.where(Tender.matches.any(TenderMatch.score >= min_score))
        count_query = count_query.where(Tender.matches.any(TenderMatch.score >= min_score))

    items = db.execute(query.limit(limit)).unique().scalars().all()
    total = db.execute(count_query).scalar_one()
    return items, total


def get_tender_detail(db: Session, tender_id: int) -> Tender | None:
    return db.execute(
        select(Tender)
        .options(
            joinedload(Tender.source),
            selectinload(Tender.documents).selectinload(TenderDocument.texts),
            selectinload(Tender.enrichments),
            selectinload(Tender.matches),
            selectinload(Tender.states),
            selectinload(Tender.alerts),
        )
        .where(Tender.id == tender_id)
    ).scalar_one_or_none()


def list_saved_tenders(db: Session, *, user_id: int, limit: int = 100) -> tuple[list[Tender], int]:
    tracked_states = ("saved", "evaluating", "presenting")
    query = (
        select(Tender)
        .join(TenderState, TenderState.tender_id == Tender.id)
        .options(
            joinedload(Tender.source),
            selectinload(Tender.matches),
            selectinload(Tender.states),
            selectinload(Tender.alerts),
        )
        .where(TenderState.user_id == user_id, TenderState.state.in_(tracked_states))
        .order_by(TenderState.updated_at.desc(), Tender.id.desc())
    )
    count_query = (
        select(func.count())
        .select_from(Tender)
        .join(TenderState, TenderState.tender_id == Tender.id)
        .where(TenderState.user_id == user_id, TenderState.state.in_(tracked_states))
    )
    items = db.execute(query.limit(limit)).unique().scalars().all()
    total = db.execute(count_query).scalar_one()
    return items, total
