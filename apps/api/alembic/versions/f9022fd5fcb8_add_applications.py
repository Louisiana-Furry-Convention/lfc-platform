"""add applications

Revision ID: f9022fd5fcb8
Revises: ddddfd9a6d9c
Create Date: 2026-03-18 01:35:29.099789

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f9022fd5fcb8"
down_revision: Union[str, Sequence[str], None] = "ddddfd9a6d9c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("applications", sa.Column("title", sa.String(), nullable=True))
    op.add_column("applications", sa.Column("target_department", sa.String(), nullable=True))
    op.add_column("applications", sa.Column("target_role", sa.String(), nullable=True))
    op.add_column("applications", sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("applications", sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True))

    op.execute("UPDATE applications SET title = 'Application' WHERE title IS NULL")
    op.execute("UPDATE applications SET current_stage = 'submitted' WHERE current_stage IS NULL AND status = 'submitted'")

    op.create_index("ix_applications_application_type", "applications", ["application_type"], unique=False)
    op.create_index("ix_applications_current_stage", "applications", ["current_stage"], unique=False)
    op.create_index("ix_applications_event_id", "applications", ["event_id"], unique=False)
    op.create_index(
        "ix_applications_event_type_status",
        "applications",
        ["event_id", "application_type", "status"],
        unique=False,
    )
    op.create_index("ix_applications_status", "applications", ["status"], unique=False)
    op.create_index("ix_applications_user_id", "applications", ["user_id"], unique=False)

   
def downgrade() -> None:
    op.drop_index("ix_applications_user_id", table_name="applications")
    op.drop_index("ix_applications_status", table_name="applications")
    op.drop_index("ix_applications_event_type_status", table_name="applications")
    op.drop_index("ix_applications_event_id", table_name="applications")
    op.drop_index("ix_applications_current_stage", table_name="applications")
    op.drop_index("ix_applications_application_type", table_name="applications")

    op.drop_column("applications", "withdrawn_at")
    op.drop_column("applications", "submitted_at")
    op.drop_column("applications", "target_role")
    op.drop_column("applications", "target_department")
    op.drop_column("applications", "title")
