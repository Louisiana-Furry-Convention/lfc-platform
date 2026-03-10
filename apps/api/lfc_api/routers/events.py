from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from lfc_api.db.session import get_db
from lfc_api.models.event import ConventionEvent

router = APIRouter(prefix="/events", tags=["events"])

@router.get("")
def list_events(db: Session = Depends(get_db)):
    rows = db.query(ConventionEvent).all()
    return [{"id": r.id, "name": r.name} for r in rows]

@router.get("/public/{event_id}")
def public_event(event_id: str, db: Session = Depends(get_db)):
    event = db.query(ConventionEvent).filter(ConventionEvent.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return {
        "event_id": event.id,
        "name": getattr(event, "name", event.id),
        "location": getattr(event, "location", ""),
        "start_date": str(getattr(event, "start_date", "")),
        "end_date": str(getattr(event, "end_date", "")),
    }
