import io
import uuid
from datetime import datetime, timezone

import qrcode
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from lfc_api.core.deps import get_current_user
from lfc_api.core.security import hash_password
from lfc_api.core.ticketing import issue_ticket_for_order
from lfc_api.db.session import get_db
from lfc_api.models.event import ConventionEvent
from lfc_api.models.ticketing import Order, Ticket, TicketType
from lfc_api.models.user import User

router = APIRouter(prefix="/tickets", tags=["tickets"])


class IssueTestTicketIn(BaseModel):
    event_id: str = "lfc-2027"
    ticket_type_id: str = "lfc-2027-regular"
    email: EmailStr
    display_name: str = ""


class CreateOrderIn(BaseModel):
    event_id: str = "lfc-2027"
    ticket_type_id: str


class CompleteOrderIn(BaseModel):
    order_id: str


@router.get("/qr/{qr_token}")
def ticket_qr(qr_token: str):
    img = qrcode.make(qr_token)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


@router.post("/orders/create")
def create_order(
    data: CreateOrderIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket_type = (
        db.query(TicketType)
        .filter(TicketType.id == data.ticket_type_id)
        .first()
    )
    if not ticket_type:
        raise HTTPException(status_code=404, detail="Ticket type not found")

    if ticket_type.event_id != data.event_id:
        raise HTTPException(status_code=400, detail="Ticket type does not belong to event")

    if not ticket_type.is_active or not ticket_type.is_public:
        raise HTTPException(status_code=404, detail="Ticket type not available")

    order = Order(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        event_id=ticket_type.event_id,
        ticket_type_id=ticket_type.id,
        status="pending",
        total_cents=ticket_type.price_cents,
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    return {
        "ok": True,
        "order_id": order.id,
        "event_id": order.event_id,
        "ticket_type_id": order.ticket_type_id,
        "status": order.status,
        "price_cents": order.total_cents,
        "currency": ticket_type.currency,
    }


@router.post("/orders/complete")
def complete_order(
    data: CompleteOrderIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    order = db.query(Order).filter(Order.id == data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status != "paid":
        order.status = "paid"
        order.paid_at = datetime.now(timezone.utc)

    ticket = issue_ticket_for_order(db, order)
    db.commit()
    db.refresh(ticket)
    db.refresh(order)

    return {
        "ok": True,
        "order_id": order.id,
        "status": order.status,
        "ticket_id": ticket.id,
        "qr_token": ticket.qr_token,
    }


@router.get("")
def list_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 50,
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    rows = (
        db.query(Ticket, User)
        .join(User, User.id == Ticket.user_id)
        .order_by(Ticket.issued_at.desc())
        .limit(limit)
        .all()
    )

    out = []
    for ticket, user in rows:
        out.append(
            {
                "ticket_id": ticket.id,
                "status": ticket.status,
                "email": user.email,
                "display_name": getattr(user, "display_name", ""),
                "user_id": user.id,
                "order_id": ticket.order_id,
                "event_id": ticket.event_id,
                "ticket_type_id": ticket.ticket_type_id,
                "issued_at": ticket.issued_at,
            }
        )
    return out


@router.get("/public/ticket_types")
def public_ticket_types(
    event_id: str = "lfc-2027",
    db: Session = Depends(get_db),
):
    rows = (
        db.query(TicketType)
        .filter(TicketType.event_id == event_id)
        .filter(TicketType.is_active == True)
        .filter(TicketType.is_public == True)
        .all()
    )

    return [
        {
            "id": row.id,
            "event_id": row.event_id,
            "name": row.name,
            "price_cents": row.price_cents,
            "currency": row.currency,
        }
        for row in rows
    ]


@router.post("/issue_test")
def issue_test_ticket(data: IssueTestTicketIn, db: Session = Depends(get_db)):
    event = db.query(ConventionEvent).filter(ConventionEvent.id == data.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    ticket_type = (
        db.query(TicketType)
        .filter(TicketType.id == data.ticket_type_id)
        .first()
    )
    if not ticket_type or ticket_type.event_id != data.event_id:
        raise HTTPException(status_code=404, detail="Ticket type not found for event")

    email = data.email.lower()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            display_name=data.display_name,
            password_hash=hash_password("testpass123"),
            role="attendee",
            is_active=True,
        )
        db.add(user)
        db.flush()

    order = Order(
        id=str(uuid.uuid4()),
        user_id=user.id,
        event_id=data.event_id,
        ticket_type_id=ticket_type.id,
        status="paid_test",
        total_cents=ticket_type.price_cents,
    )
    db.add(order)
    db.flush()
    
    ticket = issue_ticket_for_order(db, order)

    db.commit()
    db.refresh(ticket)

    return {
        "ok": True,
        "event_id": data.event_id,
        "ticket_type_id": ticket_type.id,
        "user_id": user.id,
        "order_id": order.id,
        "ticket_id": ticket.id,
        "qr_token": ticket.qr_token,
        "price_cents": ticket_type.price_cents,
        "currency": ticket_type.currency,
    }
