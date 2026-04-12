"""phase15 tender state alert overrides

Revision ID: 20260412_000015
Revises: 20260412_000014
Create Date: 2026-04-12 19:35:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260412_000015"
down_revision = "20260412_000014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tender_states", sa.Column("alert_overrides_json", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("tender_states", "alert_overrides_json")
