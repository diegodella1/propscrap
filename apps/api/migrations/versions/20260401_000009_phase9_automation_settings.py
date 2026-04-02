"""phase9 automation settings

Revision ID: 20260401_000009
Revises: 20260401_000008
Create Date: 2026-04-01 16:10:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260401_000009"
down_revision = "20260401_000008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "automation_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("ingestion_interval_hours", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("last_run_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_run_finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_message", sa.Text(), nullable=True),
        sa.Column("last_cycle_summary", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute(
        """
        INSERT INTO automation_settings (id, is_enabled, ingestion_interval_hours)
        VALUES (1, true, 1)
        """
    )


def downgrade() -> None:
    op.drop_table("automation_settings")
