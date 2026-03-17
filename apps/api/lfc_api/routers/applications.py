import json
import uuid

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from lfc_api.core.deps import get_db, get_current_user
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


@router.get("/me")
def my_applications(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    rows = (
        db.query(Application)
        .filter(Application.user_id == current_user.id)
        .order_by(Application.created_at.desc())
        .all()
    )

    return {
        "ok": True,
        "applications": [
            {
                "id": str(row.id),
                "event_id": row.event_id,
                "application_type": row.application_type,
                "status": row.status,
                "data_json": row.data_json,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
            }
            for row in rows
        ],
    }

@router.get("/me/{application_id}")
def my_application_detail(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    row = (
        db.query(Application)
        .filter(
            Application.id == str(application_id),
            Application.user_id == current_user.id,
        )
        .first()
    )

    if not row:
        raise HTTPException(status_code=404, detail="Application not found")

    return {
        "ok": True,
        "application": {
            "id": str(row.id),
            "event_id": row.event_id,
            "application_type": row.application_type,
            "status": row.status,
            "data_json": row.data_json,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        },
    }
