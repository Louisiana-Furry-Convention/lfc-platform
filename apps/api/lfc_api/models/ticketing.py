from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    DateTime,
    func,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from lfc_api.models.base import Base


class TicketType(Base):
    __tablename__ = "ticket_types"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    event_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("events.id"), index=True
    )

    name: Mapped[str] = mapped_column(String(80), nullable=False)

    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True
    )
    event_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("events.id"), index=True
    )
    ticket_type_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("ticket_types.id"), index=True
    )

    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    total_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    clover_payment_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    clover_checkout_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        UniqueConstraint("order_id", name="uq_tickets_order_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    event_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("events.id"), index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True
    )
    ticket_type_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("ticket_types.id"), index=True
    )
    order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("orders.id"), nullable=False, index=True
    )
    qr_token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="issued")
    issued_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )


class CheckIn(Base):
    __tablename__ = "checkins"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    ticket_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tickets.id"), nullable=False, index=True
    )
    lane: Mapped[str] = mapped_column(String(40), default="main", nullable=False)

    checked_in_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    performed_by_user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=True
    )


class RFIDBand(Base):
    __tablename__ = "rfid_bands"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tag_uid: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )

    event_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("events.id"), index=True
    )
    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True, index=True
    )
    ticket_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("tickets.id"), nullable=True, index=True
    )

    status: Mapped[str] = mapped_column(String(20), default="unassigned")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    issued_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=True
    )
