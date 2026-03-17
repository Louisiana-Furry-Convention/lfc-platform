"""add review metadata to applications

Revision ID: ddddfd9a6d9c
Revises: c9f0e1c2a001
Create Date: 2026-03-17 01:57:58.725147

"""
from alembic import op
import sqlalchemy as sa

revision = 'ddddfd9a6d9c'
down_revision = 'c9f0e1c2a001'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("applications", sa.Column("reviewed_by", sa.String(length=36), nullable=True))
    op.add_column("applications", sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("applications", sa.Column("review_notes", sa.Text(), nullable=True))

def downgrade():
    op.drop_column("applications", "review_notes")
    op.drop_column("applications", "reviewed_at")
    op.drop_column("applications", "reviewed_by")
