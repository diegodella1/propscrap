"""phase16 company source scope

Revision ID: 20260412_000016
Revises: 20260412_000015
Create Date: 2026-04-12 00:16:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260412_000016"
down_revision = "20260412_000015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("company_profiles", sa.Column("source_scope_mode", sa.String(length=20), nullable=False, server_default="all_active"))
    op.create_table(
        "company_profile_sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_profile_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["company_profile_id"], ["company_profiles.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("company_profile_id", "source_id", name="uq_company_profile_source"),
    )
    op.create_index(op.f("ix_company_profile_sources_company_profile_id"), "company_profile_sources", ["company_profile_id"], unique=False)
    op.create_index(op.f("ix_company_profile_sources_source_id"), "company_profile_sources", ["source_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_company_profile_sources_source_id"), table_name="company_profile_sources")
    op.drop_index(op.f("ix_company_profile_sources_company_profile_id"), table_name="company_profile_sources")
    op.drop_table("company_profile_sources")
    op.drop_column("company_profiles", "source_scope_mode")
