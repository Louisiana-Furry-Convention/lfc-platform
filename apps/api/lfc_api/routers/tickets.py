import uuid
import secrets

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from fastapi import Depends
from lfc_api.db.session import get_db
from lfc_api.models.user import User

from lfc_api.db.session import get_db
from lfc_api.models.user import User
from lfc_api.models.event import ConventionEvent
from lfc_api.models.ticketing import TicketType, Order, Ticket
from lfc_api.core.security import hash_password

router = APIRouter(prefix="/tickets", tags=["tickets"])


class IssueTestTicketIn(BaseModel):
    event_id: str = "lfc-2027"
    ticket_type_id: str = "lfc-2027-regular"
    email: EmailStr
    display_name: str = ""

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

@router.post("/issue_test")
def issue_test_ticket(data: IssueTestTicketIn, db: Session = Depends(get_db)):
    # Validate event exists
    ev = db.query(ConventionEvent).filter(ConventionEvent.id == data.event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")

    # Validate ticket type exists (and belongs to event)
    tt = db.query(TicketType).filter(TicketType.id == data.ticket_type_id).first()
    if not tt or tt.event_id != data.event_id:
        raise HTTPException(status_code=404, detail="Ticket type not found for event")

    # Find or create user
    email = data.email.lower()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Dev-only: fixed short password to avoid bcrypt byte-length issues on Pi
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

    # Create order (simple)
    order = Order(
        id=str(uuid.uuid4()),
        user_id=user.id,
        event_id=data.event_id,
        status="paid_test",
        total_cents=tt.price_cents,
    )
    db.add(order)
    db.flush()

    # Issue ticket
    qr_token = secrets.token_urlsafe(24)
    ticket = Ticket(
        id=str(uuid.uuid4()),
        event_id=data.event_id,
        user_id=user.id,
        ticket_type_id=tt.id,
        order_id=order.id,
        qr_token=qr_token,
        status="issued",
    )
    db.add(ticket)

    db.commit()

    return {
        "ok": True,
        "event_id": data.event_id,
        "ticket_type_id": tt.id,
        "user_id": user.id,
        "order_id": order.id,
        "ticket_id": ticket.id,
        "qr_token": qr_token,
        "price_cents": tt.price_cents,
        "currency": tt.currency,
    }
