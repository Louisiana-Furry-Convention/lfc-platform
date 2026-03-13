import uuid

from sqlalchemy.orm import Session

from lfc_api.core.badge import sign_ticket
from lfc_api.models.ticketing import Order, Ticket


def issue_ticket_for_order(db: Session, order: Order) -> Ticket:
    existing_ticket = db.query(Ticket).filter(Ticket.order_id == order.id).first()
    if existing_ticket:
        return existing_ticket

    ticket = Ticket(
        id=str(uuid.uuid4()),
        event_id=order.event_id,
        user_id=order.user_id,
        ticket_type_id=order.ticket_type_id,
        order_id=order.id,
        qr_token="",
        status="issued",
    )
    db.add(ticket)
    db.flush()

    ticket.qr_token = sign_ticket(ticket.id)
    db.flush()

    return ticket
