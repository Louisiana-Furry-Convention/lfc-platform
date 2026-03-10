from sqlalchemy import String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from lfc_api.models.base import Base
from datetime import datetime

class TicketType(Base):
    __tablename__ = "ticket_types"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)   # e.g. lfc-2027-regular
    event_id: Mapped[str] = mapped_column(String(64), ForeignKey("events.id"), index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    event_id: Mapped[str] = mapped_column(String(64), ForeignKey("events.id"), index=True)
    ticket_type_id: Mapped[str] = mapped_column(String(64), ForeignKey("ticket_types.id"))
    status: Mapped[str] = mapped_column(String(20), default="created")
    total_cents: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped["DateTime"] = mapped_column(DateTime, server_default=func.now())

class Ticket(Base):
    __tablename__ = "tickets"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    event_id: Mapped[str] = mapped_column(String(64), ForeignKey("events.id"), index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    ticket_type_id: Mapped[str] = mapped_column(String(64), ForeignKey("ticket_types.id"))
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"))
    qr_token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="issued")
    issued_at: Mapped["DateTime"] = mapped_column(DateTime, server_default=func.now())

class CheckIn(Base):
    __tablename__ = "checkins"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    ticket_id: Mapped[str] = mapped_column(String(36), ForeignKey("tickets.id"), nullable=False, index=True)
    lane: Mapped[str] = mapped_column(String(40), default="main", nullable=False)

    checked_in_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    performed_by_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)

    created_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow, nullable=True)
