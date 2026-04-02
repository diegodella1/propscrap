"""phase 3 tender enrichments

Revision ID: 20260331_000003
Revises: 20260331_000002
Create Date: 2026-03-31 20:40:00
"""
from alembic import op
import sqlalchemy as sa


revision = "20260331_000003"
down_revision = "20260331_000002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tender_enrichments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tender_id", sa.Integer(), sa.ForeignKey("tenders.id"), nullable=False),
        sa.Column("llm_model", sa.String(length=100), nullable=True),
        sa.Column("summary_short", sa.Text(), nullable=True),
        sa.Column("summary_structured_json", sa.JSON(), nullable=True),
        sa.Column("key_requirements", sa.JSON(), nullable=True),
        sa.Column("risk_flags", sa.JSON(), nullable=True),
        sa.Column("extracted_deadlines", sa.JSON(), nullable=True),
        sa.Column("enrichment_status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_tender_enrichments_tender_id", "tender_enrichments", ["tender_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_tender_enrichments_tender_id", table_name="tender_enrichments")
    op.drop_table("tender_enrichments")
