from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from lfc_api.db.session import get_db
from lfc_api.core.deps import get_current_user
from lfc_api.models.user import User
from lfc_api.models.ticketing import Ticket, TicketType

router = APIRouter(prefix="/me", tags=["me"])

@router.get("")
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # return minimal safe identity info
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
        .order_by(Ticket.id.desc())
        .all()
    )

    return [
        {
            "ticket_id": t.id,
            "event_id": t.event_id,
            "ticket_type_id": t.ticket_type_id,
            "ticket_type_name": getattr(tt, "name", tt.id),
            "status": t.status,
            "qr_token": t.qr_token,
        }
        for t, tt in rows
    ]
