"""add created_at to checkins"""

from alembic import op
import sqlalchemy as sa

revision = "add_checkin_created_at"
down_revision = "2442d901da36"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "checkins",
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.execute("UPDATE checkins SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")


def downgrade() -> None:
    op.drop_column("checkins", "created_at")

