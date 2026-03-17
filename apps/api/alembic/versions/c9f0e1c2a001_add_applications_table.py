"""add applications table

Revision ID: c9f0e1c2a001
Revises: 7a1b988da385
Create Date: 2026-03-17
"""

from alembic import op
import sqlalchemy as sa


revision = "c9f0e1c2a001"
down_revision = "7a1b988da385"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "applications",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("event_id", sa.String(length=50), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("application_type", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="submitted"),
        sa.Column("data_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("applications")

