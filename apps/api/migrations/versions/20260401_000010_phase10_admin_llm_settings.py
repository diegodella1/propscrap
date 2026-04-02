"""phase10 admin llm settings

Revision ID: 20260401_000010
Revises: 20260401_000009
Create Date: 2026-04-01 16:20:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260401_000010"
down_revision = "20260401_000009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("automation_settings", sa.Column("openai_api_key_override", sa.Text(), nullable=True))
    op.add_column("automation_settings", sa.Column("openai_model_override", sa.String(length=100), nullable=True))
    op.add_column("automation_settings", sa.Column("llm_master_prompt", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("automation_settings", "llm_master_prompt")
    op.drop_column("automation_settings", "openai_model_override")
    op.drop_column("automation_settings", "openai_api_key_override")
