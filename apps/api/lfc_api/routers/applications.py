# apps/api/lfc_api/routers/applications.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from lfc_api.db.session import get_db  # adjust
from lfc_api.core.deps import get_current_user  # adjust
from lfc_api.schemas.application import (
    ApplicationCreate,
    ApplicationListItem,
    ApplicationRead,
    ApplicationWithdrawResponse,
)
from lfc_api.services.applications import (
    create_application,
    get_user_application,
    list_user_applications,
    withdraw_application,
)

router = APIRouter(tags=["applications"])


@router.post("/applications", response_model=ApplicationRead)
def post_application(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_application(db, current_user, payload)


@router.get("/me/applications", response_model=list[ApplicationListItem])
def get_my_applications(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return list_user_applications(db, current_user.id)


@router.get("/me/applications/{application_id}", response_model=ApplicationRead)
def get_my_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_user_application(db, current_user.id, application_id)


@router.post("/applications/{application_id}/withdraw", response_model=ApplicationWithdrawResponse)
def post_withdraw_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    app = withdraw_application(db, current_user.id, application_id)
    return {
        "ok": True,
        "application_id": app.id,
        "status": app.status,
        "withdrawn_at": app.withdrawn_at,
    }
