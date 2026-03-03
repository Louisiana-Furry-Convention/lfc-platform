from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from lfc_api.db.session import get_db
from lfc_api.models.event import ConventionEvent

router = APIRouter(prefix="/events", tags=["events"])

@router.get("")
def list_events(db: Session = Depends(get_db)):
    rows = db.query(ConventionEvent).all()
    return [{"id": r.id, "name": r.name} for r in rows]
