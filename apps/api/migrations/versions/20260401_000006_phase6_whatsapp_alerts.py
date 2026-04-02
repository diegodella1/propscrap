"""phase 6 whatsapp user alerts

Revision ID: 20260401_000006
Revises: 20260331_000005
Create Date: 2026-04-01 15:00:00
"""
from alembic import op
import sqlalchemy as sa


revision = "20260401_000006"
down_revision = "20260331_000005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("whatsapp_number", sa.String(length=32), nullable=True))
    op.add_column(
        "users",
        sa.Column("whatsapp_opt_in", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column("users", sa.Column("whatsapp_verified_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("alert_preferences_json", sa.JSON(), nullable=True))

    op.add_column(
        "alerts",
        sa.Column("delivery_attempts", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column("alerts", sa.Column("last_error_message", sa.Text(), nullable=True))
    op.add_column("alerts", sa.Column("provider_message_id", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("alerts", "provider_message_id")
    op.drop_column("alerts", "last_error_message")
    op.drop_column("alerts", "delivery_attempts")

    op.drop_column("users", "alert_preferences_json")
    op.drop_column("users", "whatsapp_verified_at")
    op.drop_column("users", "whatsapp_opt_in")
    op.drop_column("users", "whatsapp_number")
