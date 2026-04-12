"""phase11 cuit company data and richer source admin

Revision ID: 20260411_000011
Revises: 20260401_000010
Create Date: 2026-04-11 16:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260411_000011"
down_revision = "20260401_000010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("sources", sa.Column("scraping_mode", sa.String(length=50), nullable=False, server_default="coded"))
    op.add_column("sources", sa.Column("connector_slug", sa.String(length=100), nullable=True))
    op.add_column("sources", sa.Column("config_json", sa.JSON(), nullable=True))

    op.add_column("company_profiles", sa.Column("cuit", sa.String(length=11), nullable=True))
    op.add_column("company_profiles", sa.Column("legal_name", sa.String(length=255), nullable=True))
    op.add_column("company_profiles", sa.Column("tax_status_json", sa.JSON(), nullable=True))
    op.add_column("company_profiles", sa.Column("company_data_source", sa.String(length=100), nullable=True))
    op.add_column("company_profiles", sa.Column("company_data_updated_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_company_profiles_cuit", "company_profiles", ["cuit"], unique=True)

    op.add_column("users", sa.Column("cuit", sa.String(length=11), nullable=True))
    op.create_index("ix_users_cuit", "users", ["cuit"], unique=False)

    op.execute("UPDATE sources SET scraping_mode = 'coded' WHERE scraping_mode IS NULL")
    op.execute("UPDATE sources SET connector_slug = slug WHERE connector_slug IS NULL")

    op.alter_column("sources", "scraping_mode", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_users_cuit", table_name="users")
    op.drop_column("users", "cuit")

    op.drop_index("ix_company_profiles_cuit", table_name="company_profiles")
    op.drop_column("company_profiles", "company_data_updated_at")
    op.drop_column("company_profiles", "company_data_source")
    op.drop_column("company_profiles", "tax_status_json")
    op.drop_column("company_profiles", "legal_name")
    op.drop_column("company_profiles", "cuit")

    op.drop_column("sources", "config_json")
    op.drop_column("sources", "connector_slug")
    op.drop_column("sources", "scraping_mode")
