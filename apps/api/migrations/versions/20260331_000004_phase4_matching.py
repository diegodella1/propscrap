"""phase 4 company profile and matching

Revision ID: 20260331_000004
Revises: 20260331_000003
Create Date: 2026-03-31 21:20:00
"""
from alembic import op
import sqlalchemy as sa


revision = "20260331_000004"
down_revision = "20260331_000003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "company_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("company_description", sa.Text(), nullable=False),
        sa.Column("sectors", sa.JSON(), nullable=True),
        sa.Column("include_keywords", sa.JSON(), nullable=True),
        sa.Column("exclude_keywords", sa.JSON(), nullable=True),
        sa.Column("jurisdictions", sa.JSON(), nullable=True),
        sa.Column("preferred_buyers", sa.JSON(), nullable=True),
        sa.Column("min_amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("max_amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("alert_preferences_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "tender_matches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tender_id", sa.Integer(), sa.ForeignKey("tenders.id"), nullable=False),
        sa.Column("company_profile_id", sa.Integer(), sa.ForeignKey("company_profiles.id"), nullable=False),
        sa.Column("score", sa.Numeric(5, 2), nullable=False),
        sa.Column("score_band", sa.String(length=20), nullable=False),
        sa.Column("reasons_json", sa.JSON(), nullable=True),
        sa.Column("matched_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_index("ix_tender_matches_tender_id", "tender_matches", ["tender_id"], unique=False)
    op.create_index(
        "ix_tender_matches_company_profile_id",
        "tender_matches",
        ["company_profile_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_tender_matches_company_profile_id", table_name="tender_matches")
    op.drop_index("ix_tender_matches_tender_id", table_name="tender_matches")
    op.drop_table("tender_matches")
    op.drop_table("company_profiles")
