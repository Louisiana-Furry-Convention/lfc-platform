import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from lfc_api.db.session import get_db
from lfc_api.core.deps import get_current_user
from lfc_api.models.user import User
from lfc_api.models.ticketing import Ticket, RFIDBand

router = APIRouter(prefix="/rfid", tags=["rfid"])


class AssignRFIDIn(BaseModel):
    ticket_id: str
    tag_uid: str


@router.post("/assign")
def assign_rfid(
    data: AssignRFIDIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["admin", "staff", "checkin"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    ticket = db.query(Ticket).filter(Ticket.id == data.ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    band = db.query(RFIDBand).filter(RFIDBand.tag_uid == data.tag_uid).first()

    if band:
        if band.ticket_id and band.ticket_id != ticket.id:
            raise HTTPException(status_code=400, detail="RFID band already assigned to another ticket")

        band.event_id = ticket.event_id
        band.user_id = ticket.user_id
        band.ticket_id = ticket.id
        band.status = "assigned"
        band.is_active = True
        band.issued_at = datetime.utcnow()
    else:
        band = RFIDBand(
            id=str(uuid.uuid4()),
            tag_uid=data.tag_uid,
            event_id=ticket.event_id,
            user_id=ticket.user_id,
            ticket_id=ticket.id,
            status="assigned",
            is_active=True,
            issued_at=datetime.utcnow(),
        )
        db.add(band)

    db.commit()

    return {
        "ok": True,
        "band_id": band.id,
        "tag_uid": band.tag_uid,
        "ticket_id": band.ticket_id,
        "user_id": band.user_id,
        "status": band.status,
        "is_active": band.is_active,
    }
