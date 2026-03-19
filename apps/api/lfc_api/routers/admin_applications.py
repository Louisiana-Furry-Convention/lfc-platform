# apps/api/lfc_api/routers/admin_applications.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from lfc_api.db.session import get_db  # adjust
from lfc_api.core.deps import get_current_user  # adjust
from lfc_api.core.authz import require_roles  # adjust
from lfc_api.schemas.application import (
    ApplicationListItem,
    ApplicationRead,
    ApplicationStageUpdate,
    ApplicationStatusUpdate,
)
from lfc_api.schemas.application_review import ApplicationReviewCreate, ApplicationReviewRead
from lfc_api.services.applications import (
    create_application_review,
    get_admin_application,
    list_admin_applications,
    update_application_stage,
    update_application_status,
)

router = APIRouter(tags=["admin-applications"])


@router.get("/admin/applications", response_model=list[ApplicationListItem])
def admin_list_applications(
    status: str | None = Query(default=None),
    application_type: str | None = Query(default=None),
    event_id: str | None = Query(default=None),
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "officer", "director")),
):
    return list_admin_applications(
        db,
        status=status,
        application_type=application_type,
        event_id=event_id,
        limit=limit,
        offset=offset,
    )


@router.get("/admin/applications/{application_id}", response_model=ApplicationRead)
def admin_get_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "officer", "director")),
):
    return get_admin_application(db, application_id)


@router.patch("/admin/applications/{application_id}/status", response_model=ApplicationRead)
def admin_patch_application_status(
    application_id: str,
    payload: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "officer", "director")),
):
    return update_application_status(db, application_id, payload.status, current_user)


@router.patch("/admin/applications/{application_id}/stage", response_model=ApplicationRead)
def admin_patch_application_stage(
    application_id: str,
    payload: ApplicationStageUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "officer", "director")),
):
    return update_application_stage(db, application_id, payload.current_stage, current_user)


@router.post("/admin/applications/{application_id}/reviews", response_model=ApplicationReviewRead)
def admin_post_application_review(
    application_id: str,
    payload: ApplicationReviewCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "officer", "director")),
):
    return create_application_review(db, application_id, current_user, payload)
