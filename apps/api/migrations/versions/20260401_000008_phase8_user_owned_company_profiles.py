"""phase 8 user owned company profiles

Revision ID: 20260401_000008
Revises: 20260401_000007
Create Date: 2026-04-01 18:30:00
"""
from alembic import op
import sqlalchemy as sa


revision = "20260401_000008"
down_revision = "20260401_000007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("company_profile_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_users_company_profile_id",
        "users",
        "company_profiles",
        ["company_profile_id"],
        ["id"],
    )
    op.create_index("ix_users_company_profile_id", "users", ["company_profile_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_users_company_profile_id", table_name="users")
    op.drop_constraint("fk_users_company_profile_id", "users", type_="foreignkey")
    op.drop_column("users", "company_profile_id")
