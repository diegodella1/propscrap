"""phase 5 workflow states and alerts

Revision ID: 20260331_000005
Revises: 20260331_000004
Create Date: 2026-03-31 22:05:00
"""
from alembic import op
import sqlalchemy as sa


revision = "20260331_000005"
down_revision = "20260331_000004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "tender_states",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tender_id", sa.Integer(), sa.ForeignKey("tenders.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("state", sa.String(length=50), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tender_id", sa.Integer(), sa.ForeignKey("tenders.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("alert_type", sa.String(length=50), nullable=False),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivery_channel", sa.String(length=50), nullable=False, server_default="dashboard"),
        sa.Column("delivery_status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("payload_snapshot", sa.JSON(), nullable=True),
    )

    op.create_index("ix_tender_states_tender_id", "tender_states", ["tender_id"], unique=False)
    op.create_index("ix_alerts_tender_id", "alerts", ["tender_id"], unique=False)
    op.create_index("ix_alerts_user_id", "alerts", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_alerts_user_id", table_name="alerts")
    op.drop_index("ix_alerts_tender_id", table_name="alerts")
    op.drop_index("ix_tender_states_tender_id", table_name="tender_states")
    op.drop_table("alerts")
    op.drop_table("tender_states")
    op.drop_table("users")
