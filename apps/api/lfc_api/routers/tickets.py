import uuid
import secrets
import io
import qrcode

from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from lfc_api.db.session import get_db
from lfc_api.models.user import User

from lfc_api.models.event import ConventionEvent
from lfc_api.models.ticketing import TicketType, Order, Ticket
from lfc_api.core.security import hash_password
from lfc_api.core.badge import sign_ticket
from lfc_api.core.deps import get_current_user

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
    tt = db.query(TicketType).filter(TicketType.id == data.ticket_type_id).first()
    if (
       not tt
       or tt.event_id != data.event_id
       or not getattr(tt, "is_active", True)
       or not getattr(tt, "is_public", True)
   ):
       raise HTTPException(status_code=404, detail="Ticket type not available")

    order = Order(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        event_id=data.event_id,
        ticket_type_id=data.ticket_type_id,
        status="pending",
        total_cents=tt.price_cents,
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
       "price_cents": tt.price_cents,
       "currency": tt.currency,
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

    existing_ticket = db.query(Ticket).filter(Ticket.order_id == order.id).first()
    if existing_ticket:
       if order.status != "paid":
           order.status = "paid"
           db.commit()
       return {
           "ok": True,
           "order_id": order.id,
           "status": order.status,
           "ticket_id": existing_ticket.id,
           "qr_token": existing_ticket.qr_token,
       }

    if order.status == "paid":
       raise HTTPException(status_code=400, detail="Order is paid but no ticket exists")

    tt = db.query(TicketType).filter(TicketType.id == order.ticket_type_id).first()
    if not tt:
        raise HTTPException(status_code=404, detail="Ticket type not found")

    qr_token = secrets.token_urlsafe(24)

    ticket = Ticket(
        id=str(uuid.uuid4()),
        event_id=order.event_id,
        user_id=order.user_id,
        ticket_type_id=order.ticket_type_id,
        order_id=order.id,
        qr_token=qr_token,
        status="issued",
    )
    db.add(ticket)

    order.status = "paid"
    db.commit()

    return {
        "ok": True,
        "order_id": order.id,
        "status": order.status,
        "ticket_id": ticket.id,
        "qr_token": qr_token,
    }

@router.get("")
def list_tickets(db: Session = Depends(get_db), limit: int = 50):
    rows = (
        db.query(Ticket, User)
        .join(User, User.id == Ticket.user_id)
        .order_by(Ticket.created_at.desc() if hasattr(Ticket, "created_at") else Ticket.id.desc())
        .limit(limit)
        .all()
    )

    out = []
    for t, u in rows:
        out.append(
            {
                "ticket_id": t.id,
                "status": getattr(t, "status", "unknown"),
                "email": u.email,
                "display_name": getattr(u, "display_name", ""),
                "user_id": u.id,
            }
        )
    return out

@router.get("/public/ticket_types")
def public_ticket_types(event_id: str = "lfc-2027", db: Session = Depends(get_db)):
    rows = (
        db.query(TicketType)
        .filter(TicketType.event_id == event_id)
        .filter(TicketType.is_active == True)
        .filter(TicketType.is_public == True)
        .all()
    )

    return [
        {
            "id": r.id,
            "event_id": r.event_id,
            "name": getattr(r, "name", r.id),
            "price_cents": r.price_cents,
            "currency": r.currency,
        }
        for r in rows
    ]

@router.post("/issue_test")
def issue_test_ticket(data: IssueTestTicketIn, db: Session = Depends(get_db)):
    # Validate event exists
    ev = db.query(ConventionEvent).filter(ConventionEvent.id == data.event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")

    # Validate ticket type exists
    tt = db.query(TicketType).filter(TicketType.id == data.ticket_type_id).first()
    if not tt or tt.event_id != data.event_id:
        raise HTTPException(status_code=404, detail="Ticket type not found for event")

    # Find or create user
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

    # Create order
    order = Order(
        id=str(uuid.uuid4()),
        user_id=user.id,
        event_id=data.event_id,
        ticket_type_id=data.ticket_type_id,
        status="paid_test",
        total_cents=tt.price_cents,
    )
    db.add(order)
    db.flush()

    # Create ticket first, then sign its id
    ticket = Ticket(
        id=str(uuid.uuid4()),
        event_id=data.event_id,
        user_id=user.id,
        ticket_type_id=tt.id,
        order_id=order.id,
        qr_token="",   # temporary
        status="issued",
    )
    db.add(ticket)
    db.flush()

    ticket.qr_token = sign_ticket(ticket.id)

    db.commit()

    return {
        "ok": True,
        "event_id": data.event_id,
        "ticket_type_id": tt.id,
        "user_id": user.id,
        "order_id": order.id,
        "ticket_id": ticket.id,
        "qr_token": ticket.qr_token,
        "price_cents": tt.price_cents,
        "currency": tt.currency,
    }
