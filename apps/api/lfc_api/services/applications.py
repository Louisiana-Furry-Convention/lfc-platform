# apps/api/lfc_api/services/applications.py

from datetime import datetime, UTC
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from lfc_api.core.application_constants import (
    APPLICATION_STATUS_WITHDRAWN,
    TERMINAL_APPLICATION_STATUSES,
    default_stage_for_type,
    is_valid_application_stage,
    is_valid_application_status,
)
from lfc_api.models.application import Application
from lfc_api.models.application_review import ApplicationReview


def utcnow() -> datetime:
    return datetime.now(UTC)


def create_application(db: Session, user, payload):
    now = utcnow()

    application = Application(
        id=str(uuid4()),
        event_id=payload.event_id,
        user_id=user.id,
        application_type=payload.application_type,
        status=payload.status,
        current_stage=default_stage_for_type(payload.application_type, payload.status),
        title=payload.title,
        target_department=payload.target_department,
        target_role=payload.target_role,
        data_json=payload.data_json,
        submitted_at=now if payload.status == "submitted" else None,
        withdrawn_at=None,
        created_at=now,
        updated_at=now,
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def list_user_applications(db: Session, user_id: str):
    stmt = (
        select(Application)
        .where(Application.user_id == user_id)
        .order_by(Application.created_at.desc())
    )
    return db.execute(stmt).scalars().all()


def get_user_application(db: Session, user_id: str, application_id: str):
    stmt = select(Application).where(
        Application.id == application_id,
        Application.user_id == user_id,
    )
    app = db.execute(stmt).scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="application not found")
    return app


def withdraw_application(db: Session, user_id: str, application_id: str):
    app = get_user_application(db, user_id, application_id)

    if app.status in TERMINAL_APPLICATION_STATUSES:
        raise HTTPException(status_code=400, detail="application is already terminal")

    now = utcnow()
    app.status = APPLICATION_STATUS_WITHDRAWN
    app.withdrawn_at = now
    app.updated_at = now

    db.add(app)
    db.commit()
    db.refresh(app)
    return app


def list_admin_applications(
    db: Session,
    *,
    status: str | None = None,
    application_type: str | None = None,
    event_id: str | None = None,
    limit: int = 100,
    offset: int = 0,
):
    stmt = select(Application)

    if status:
        stmt = stmt.where(Application.status == status)
    if application_type:
        stmt = stmt.where(Application.application_type == application_type)
    if event_id:
        stmt = stmt.where(Application.event_id == event_id)

    stmt = stmt.order_by(Application.created_at.desc()).limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()


def get_admin_application(db: Session, application_id: str):
    stmt = select(Application).where(Application.id == application_id)
    app = db.execute(stmt).scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="application not found")
    return app


def update_application_status(db: Session, application_id: str, status: str, actor):
    if not is_valid_application_status(status):
        raise HTTPException(status_code=400, detail="invalid status")

    app = get_admin_application(db, application_id)
    app.status = status
    app.updated_at = utcnow()

    db.add(app)
    db.commit()
    db.refresh(app)
    return app


def update_application_stage(db: Session, application_id: str, stage: str, actor):
    if not is_valid_application_stage(stage):
        raise HTTPException(status_code=400, detail="invalid stage")

    app = get_admin_application(db, application_id)
    app.current_stage = stage
    app.updated_at = utcnow()

    db.add(app)
    db.commit()
    db.refresh(app)
    return app


def create_application_review(db: Session, application_id: str, actor, payload):
    app = get_admin_application(db, application_id)

    review = ApplicationReview(
        id=str(uuid4()),
        application_id=app.id,
        stage=payload.stage,
        decision=payload.decision,
        reviewed_by_user_id=actor.id,
        notes=payload.notes,
        created_at=utcnow(),
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review
