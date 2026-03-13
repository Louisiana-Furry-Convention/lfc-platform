from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from lfc_api.core.deps import get_current_user
from lfc_api.db.session import get_db
from lfc_api.models.ticketing import Order, Ticket, TicketType
from lfc_api.models.user import User

router = APIRouter(prefix="/me", tags=["me"])


@router.get("")
def me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "display_name": getattr(current_user, "display_name", ""),
        "role": current_user.role,
        "is_active": current_user.is_active,
    }


@router.get("/tickets")
def my_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(Ticket, TicketType)
        .join(TicketType, TicketType.id == Ticket.ticket_type_id)
        .filter(Ticket.user_id == current_user.id)
        .order_by(Ticket.issued_at.desc())
        .all()
    )

    return [
        {
            "ticket_id": ticket.id,
            "order_id": ticket.order_id,
            "event_id": ticket.event_id,
            "ticket_type_id": ticket.ticket_type_id,
            "ticket_type_name": getattr(ticket_type, "name", ticket_type.id),
            "status": ticket.status,
            "qr_token": ticket.qr_token,
            "issued_at": ticket.issued_at,
        }
        for ticket, ticket_type in rows
    ]


@router.get("/orders")
def my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(Order, TicketType)
        .join(TicketType, TicketType.id == Order.ticket_type_id)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )

    return [
        {
            "order_id": order.id,
            "event_id": order.event_id,
            "ticket_type_id": order.ticket_type_id,
            "ticket_type_name": getattr(ticket_type, "name", ticket_type.id),
            "status": order.status,
            "total_cents": order.total_cents,
            "currency": getattr(ticket_type, "currency", "USD"),
            "clover_checkout_id": order.clover_checkout_id,
            "clover_payment_id": order.clover_payment_id,
            "created_at": order.created_at,
            "paid_at": order.paid_at,
        }
        for order, ticket_type in rows
    ]
