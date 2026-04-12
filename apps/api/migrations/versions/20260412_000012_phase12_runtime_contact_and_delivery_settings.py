"""phase12 runtime contact and delivery settings

Revision ID: 20260412_000012
Revises: 20260411_000011
Create Date: 2026-04-12 10:30:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260412_000012"
down_revision = "20260411_000011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("automation_settings", sa.Column("contact_email", sa.String(length=255), nullable=True))
    op.add_column("automation_settings", sa.Column("contact_whatsapp_number", sa.String(length=50), nullable=True))
    op.add_column("automation_settings", sa.Column("contact_telegram_handle", sa.String(length=100), nullable=True))
    op.add_column("automation_settings", sa.Column("demo_booking_url", sa.Text(), nullable=True))
    op.add_column("automation_settings", sa.Column("resend_api_key_override", sa.Text(), nullable=True))
    op.add_column("automation_settings", sa.Column("resend_from_email", sa.String(length=255), nullable=True))
    op.add_column(
        "automation_settings",
        sa.Column("email_delivery_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("automation_settings", "email_delivery_enabled", server_default=None)


def downgrade() -> None:
    op.drop_column("automation_settings", "email_delivery_enabled")
    op.drop_column("automation_settings", "resend_from_email")
    op.drop_column("automation_settings", "resend_api_key_override")
    op.drop_column("automation_settings", "demo_booking_url")
    op.drop_column("automation_settings", "contact_telegram_handle")
    op.drop_column("automation_settings", "contact_whatsapp_number")
    op.drop_column("automation_settings", "contact_email")
