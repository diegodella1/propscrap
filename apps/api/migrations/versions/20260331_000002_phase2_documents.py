"""phase 2 documents and detail cache

Revision ID: 20260331_000002
Revises: 20260331_000001
Create Date: 2026-03-31 20:10:00
"""
from alembic import op
import sqlalchemy as sa


revision = "20260331_000002"
down_revision = "20260331_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tenders", sa.Column("detail_html_path", sa.Text(), nullable=True))
    op.add_column("tenders", sa.Column("detail_cached_at", sa.DateTime(timezone=True), nullable=True))

    op.create_table(
        "tender_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tender_id", sa.Integer(), sa.ForeignKey("tenders.id"), nullable=False),
        sa.Column("document_type", sa.String(length=100), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("download_status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("downloaded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "document_texts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tender_document_id", sa.Integer(), sa.ForeignKey("tender_documents.id"), nullable=False),
        sa.Column("extraction_method", sa.String(length=50), nullable=False),
        sa.Column("extraction_status", sa.String(length=50), nullable=False),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column("text_length", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("confidence_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_index("ix_tender_documents_tender_id", "tender_documents", ["tender_id"], unique=False)
    op.create_index(
        "ix_document_texts_tender_document_id",
        "document_texts",
        ["tender_document_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_document_texts_tender_document_id", table_name="document_texts")
    op.drop_index("ix_tender_documents_tender_id", table_name="tender_documents")
    op.drop_table("document_texts")
    op.drop_table("tender_documents")
    op.drop_column("tenders", "detail_cached_at")
    op.drop_column("tenders", "detail_html_path")
