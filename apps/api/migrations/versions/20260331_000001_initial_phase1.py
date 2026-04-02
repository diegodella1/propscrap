"""initial phase 1 schema

Revision ID: 20260331_000001
Revises:
Create Date: 2026-03-31 19:30:00
"""
from alembic import op
import sqlalchemy as sa


revision = "20260331_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("base_url", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("slug"),
    )

    op.create_table(
        "source_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("items_found", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("items_new", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
    )

    op.create_table(
        "tenders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description_raw", sa.Text(), nullable=True),
        sa.Column("organization", sa.String(length=255), nullable=True),
        sa.Column("jurisdiction", sa.String(length=255), nullable=True),
        sa.Column("procedure_type", sa.String(length=100), nullable=True),
        sa.Column("publication_date", sa.Date(), nullable=True),
        sa.Column("deadline_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("opening_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("estimated_amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("dedupe_hash", sa.String(length=64), nullable=False),
        sa.Column("status_raw", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_index("ix_tenders_source_external", "tenders", ["source_id", "external_id"], unique=False)
    op.create_index("ix_tenders_dedupe_hash", "tenders", ["dedupe_hash"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_tenders_dedupe_hash", table_name="tenders")
    op.drop_index("ix_tenders_source_external", table_name="tenders")
    op.drop_table("tenders")
    op.drop_table("source_runs")
    op.drop_table("sources")
