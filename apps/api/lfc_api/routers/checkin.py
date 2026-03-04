import uuid, json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from lfc_api.db.session import get_db
from lfc_api.models.user import User
from lfc_api.models.ticketing import Ticket, CheckIn
from lfc_api.models.ledger import DomainEvent
from lfc_api.core.deps import get_current_user

router = APIRouter(prefix="/checkin", tags=["checkin"])

class CheckInIn(BaseModel):
    qr_token: str
    lane: str = "main"

@router.post("")
def check_in(
    data: CheckInIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # must be active staff/checkin/admin
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    if current_user.role not in {"staff", "checkin", "admin"}:
        raise HTTPException(status_code=403, detail="Not authorized")

    t = db.query(Ticket).filter(Ticket.qr_token == data.qr_token).first()
    if not t:
        raise HTTPException(status_code=404, detail="Invalid QR")

    ci = CheckIn(
        id=str(uuid.uuid4()),
        ticket_id=t.id,
        performed_by_user_id=current_user.id,
        lane=data.lane,
    )
    db.add(ci)

    ev = DomainEvent(
        event_type="ticket.checked_in",
        aggregate_type="ticket",
        aggregate_id=t.id,
        payload_json=json.dumps({"lane": data.lane, "qr_token": data.qr_token}),
        source="edge",
    )
    db.add(ev)

    try:
        t.status = "checked_in"
        db.commit()
    except IntegrityError:
        db.rollback()
        return {"ok": True, "status": "already_checked_in", "ticket_id": t.id}

    return {"ok": True, "status": "checked_in", "ticket_id": t.id}
