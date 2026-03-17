import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from lfc_api.core.deps import get_current_user
from lfc_api.db.session import get_db
from lfc_api.models.application import Application

router = APIRouter(prefix="/applications", tags=["applications"])


class ApplicationCreate(BaseModel):
    event_id: str
    application_type: str
    data: dict


@router.post("")
def create_application(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    allowed_types = {"staff", "vendor", "panel"}
    if payload.application_type not in allowed_types:
        raise HTTPException(status_code=400, detail="invalid application_type")

    app = Application(
        id=str(uuid.uuid4()),
        event_id=payload.event_id,
        user_id=current_user.id,
        application_type=payload.application_type,
        status="submitted",
        data_json=json.dumps(payload.data),
    )

    db.add(app)
    db.commit()
    db.refresh(app)

    return {
        "ok": True,
        "application_id": str(app.id),
        "status": app.status,
    }
