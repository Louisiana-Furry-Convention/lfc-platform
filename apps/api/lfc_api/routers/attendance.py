from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from lfc_api.db.session import get_db
from lfc_api.core.deps import get_current_user
from lfc_api.models.ticketing import Ticket, CheckIn, TicketType

router = APIRouter(prefix="/attendance", tags=["attendance"])

@router.get("/live")
def live_attendance(
    event_id: str = "lfc-2027",
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    issued = db.query(func.count(Ticket.id)).filter(
        Ticket.event_id == event_id
    ).scalar() or 0

    checked_in = (
        db.query(func.count(CheckIn.id))
        .join(Ticket, Ticket.id == CheckIn.ticket_id)
        .filter(Ticket.event_id == event_id)
        .scalar()
        or 0
    )

    tiers = (
        db.query(
            TicketType.name,
            func.count(CheckIn.id)
        )
        .join(Ticket, Ticket.ticket_type_id == TicketType.id)
        .join(CheckIn, CheckIn.ticket_id == Ticket.id)
        .filter(Ticket.event_id == event_id)
        .group_by(TicketType.name)
        .all()
    )

    tier_counts = {name: count for name, count in tiers}

    return {
        "event_id": event_id,
        "tickets_issued": issued,
        "checked_in": checked_in,
        "inside_venue": checked_in,
        "tiers": tier_counts
    }
