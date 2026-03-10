"""add ticket types and stats"""

from alembic import op
import sqlalchemy as sa


revision = "2442d901da36"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "domain_events",
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
    )
    op.add_column(
        "events",
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
    )
    op.add_column(
        "orders",
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
    )
    op.add_column(
        "tickets",
        sa.Column("issued_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
    )
    op.add_column(
        "checkins",
        sa.Column("checked_in_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
    )

    op.execute("UPDATE domain_events SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
    op.execute("UPDATE events SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
    op.execute("UPDATE orders SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
    op.execute("UPDATE tickets SET issued_at = CURRENT_TIMESTAMP WHERE issued_at IS NULL")
    op.execute("UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
    op.execute("UPDATE checkins SET checked_in_at = CURRENT_TIMESTAMP WHERE checked_in_at IS NULL")

    op.create_table(
        "ticket_types",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("event_id", sa.String(length=64), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("price_cents", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False, server_default="USD"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ticket_types_event_id", "ticket_types", ["event_id"], unique=False)
    op.create_index("ix_ticket_types_code", "ticket_types", ["code"], unique=False)


def downgrade():
    op.drop_index("ix_ticket_types_code", table_name="ticket_types")
    op.drop_index("ix_ticket_types_event_id", table_name="ticket_types")
    op.drop_table("ticket_types")

    op.drop_column("checkins", "checked_in_at")
    op.drop_column("users", "created_at")
    op.drop_column("tickets", "issued_at")
    op.drop_column("orders", "created_at")
    op.drop_column("events", "created_at")
    op.drop_column("domain_events", "created_at")
