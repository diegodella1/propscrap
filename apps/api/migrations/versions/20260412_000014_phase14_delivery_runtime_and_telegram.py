"""phase14 delivery runtime and telegram

Revision ID: 20260412_000014
Revises: 20260412_000013
Create Date: 2026-04-12 12:15:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260412_000014"
down_revision = "20260412_000013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("telegram_chat_id", sa.String(length=64), nullable=True))
    op.add_column("users", sa.Column("telegram_opt_in", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("users", sa.Column("telegram_verified_at", sa.DateTime(timezone=True), nullable=True))

    op.add_column("automation_settings", sa.Column("whatsapp_enabled_override", sa.Boolean(), nullable=True))
    op.add_column("automation_settings", sa.Column("whatsapp_provider_override", sa.String(length=50), nullable=True))
    op.add_column("automation_settings", sa.Column("whatsapp_meta_token_override", sa.Text(), nullable=True))
    op.add_column("automation_settings", sa.Column("whatsapp_meta_phone_number_id_override", sa.String(length=255), nullable=True))
    op.add_column("automation_settings", sa.Column("whatsapp_meta_api_version_override", sa.String(length=50), nullable=True))
    op.add_column("automation_settings", sa.Column("telegram_enabled_override", sa.Boolean(), nullable=True))
    op.add_column("automation_settings", sa.Column("telegram_bot_token_override", sa.Text(), nullable=True))

    op.alter_column("users", "telegram_opt_in", server_default=None)


def downgrade() -> None:
    op.drop_column("automation_settings", "telegram_bot_token_override")
    op.drop_column("automation_settings", "telegram_enabled_override")
    op.drop_column("automation_settings", "whatsapp_meta_api_version_override")
    op.drop_column("automation_settings", "whatsapp_meta_phone_number_id_override")
    op.drop_column("automation_settings", "whatsapp_meta_token_override")
    op.drop_column("automation_settings", "whatsapp_provider_override")
    op.drop_column("automation_settings", "whatsapp_enabled_override")

    op.drop_column("users", "telegram_verified_at")
    op.drop_column("users", "telegram_opt_in")
    op.drop_column("users", "telegram_chat_id")
