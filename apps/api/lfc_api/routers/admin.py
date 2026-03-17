import uuid

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session, aliased
from datetime import datetime, timedelta
from sqlalchemy import func

from lfc_api.db.session import get_db
from lfc_api.models.user import User
from lfc_api.models.ticketing import CheckIn, Ticket, TicketType
from lfc_api.models.application import Application

from lfc_api.core.deps import get_current_user
from lfc_api.core.authz import require_roles
from lfc_api.core.security import hash_password

router = APIRouter(prefix="/admin", tags=["admin"])

APPLICATION_STATUSES = {
    "submitted",
    "under_review",
    "approved",
    "denied",
    "waitlisted",
}

APPLICATION_REVIEW_ROLES = ["admin", "officer", "director"]

class CreateStaffIn(BaseModel):
    email: EmailStr
    display_name: str = ""
    password: str = "staffpass123"
    role: str = "staff"  # allowed: staff, checkin, admin


class PromoteIn(BaseModel):
    user_id: str
    role: str  # staff | checkin | admin
    is_active: bool = True

class CreateTicketTypeIn(BaseModel):
    id: str
    event_id: str = "lfc-2027"
    name: str
    price_cents: int
    currency: str = "USD"
    is_active: bool = True

class ApplicationStatusUpdate(BaseModel):
    status: str
    review_notes: str | None = None

class UpdateTicketTypeIn(BaseModel):
    name: str | None = None
    price_cents: int | None = None
    currency: str | None = None
    is_active: bool | None = None

@router.get("/users")
def list_users(
    q: str = "",
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_roles(current_user, ["admin"])

    query = db.query(User)
    if q:
        qq = f"%{q.lower()}%"
        query = query.filter(User.email.ilike(qq))

    rows = query.order_by(User.created_at.desc()).limit(limit).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "display_name": u.display_name,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": str(u.created_at),
        }
        for u in rows
    ]


@router.post("/promote")
def promote_user(
    data: PromoteIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_roles(current_user, ["admin"])

    role = data.role.lower().strip()
    if role not in {"staff", "checkin", "admin"}:
        raise HTTPException(status_code=400, detail="Invalid role")

    u = db.query(User).filter(User.id == data.user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")

    u.role = role
    u.is_active = bool(data.is_active)
    db.commit()
    return {"ok": True, "user_id": u.id, "role": u.role, "is_active": u.is_active}

@router.get("/checkins")
def recent_checkins(
    event_id: str = "lfc-2027",
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_roles(current_user, ["admin"])

    rows = (
        db.query(CheckIn, Ticket, User)
        .join(Ticket, Ticket.id == CheckIn.ticket_id)
        .join(User, User.id == Ticket.user_id)
        .filter(Ticket.event_id == event_id)
        .order_by(CheckIn.created_at.desc(), CheckIn.id.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "checkin_id": ci.id,
            "created_at": ci.created_at.isoformat() if ci.created_at else None,
            "ticket_id": t.id,
            "event_id": t.event_id,
            "ticket_type_id": t.ticket_type_id,
            "email": u.email,
            "display_name": u.display_name,
        }
        for ci, t, u in rows
    ]

@router.get("/stats")
def admin_stats(
    event_id: str = "lfc-2027",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_roles(current_user, ["admin"])

    issued = db.query(func.count(Ticket.id)).filter(Ticket.event_id == event_id).scalar() or 0

    checked_in = (
        db.query(func.count(CheckIn.id))
        .join(Ticket, Ticket.id == CheckIn.ticket_id)
        .filter(Ticket.event_id == event_id)
        .scalar()
        or 0
    )

    issued_by_type_rows = (
        db.query(TicketType.name, func.count(Ticket.id))
        .join(Ticket, Ticket.ticket_type_id == TicketType.id)
        .filter(Ticket.event_id == event_id)
        .group_by(TicketType.name)
        .all()
    )

    checked_in_by_type_rows = (
        db.query(TicketType.name, func.count(CheckIn.id))
        .join(Ticket, Ticket.ticket_type_id == TicketType.id)
        .join(CheckIn, CheckIn.ticket_id == Ticket.id)
        .filter(Ticket.event_id == event_id)
        .group_by(TicketType.name)
        .all()
    )

    return {
        "event_id": event_id,
        "tickets_issued": int(issued),
        "checked_in": int(checked_in),
        "issued_by_type": {name: int(count) for name, count in issued_by_type_rows},
        "checked_in_by_type": {name: int(count) for name, count in checked_in_by_type_rows},
    }

@router.get("/ticket_types")
def admin_ticket_types(
    event_id: str = "lfc-2027",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_roles(current_user, ["admin"])

    rows = (
        db.query(TicketType)
        .filter(TicketType.event_id == event_id)
        .order_by(TicketType.id.asc())
        .all()
    )

    return [
        {
            "id": t.id,
            "event_id": t.event_id,
            "name": t.name,
            "price_cents": t.price_cents,
            "currency": t.currency,
            "is_active": getattr(t, "is_active", True),
        }
        for t in rows
    ]


@router.post("/ticket_types")
def create_ticket_type(
    data: CreateTicketTypeIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_roles(current_user, ["admin"])

    existing = db.query(TicketType).filter(TicketType.id == data.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ticket type id already exists")

    ticket_type = TicketType(
        id=data.id.strip(),
        event_id=data.event_id,
        name=data.name.strip(),
        price_cents=data.price_cents,
        currency=data.currency.upper().strip(),
        is_active=bool(data.is_active),
    )
    db.add(ticket_type)
    db.commit()

    return {
        "ok": True,
        "id": ticket_type.id,
        "event_id": ticket_type.event_id,
        "name": ticket_type.name,
        "price_cents": ticket_type.price_cents,
        "currency": ticket_type.currency,
        "is_active": getattr(ticket_type, "is_active", True),
    }


@router.patch("/ticket_types/{ticket_type_id}")
def update_ticket_type(
    ticket_type_id: str,
    data: UpdateTicketTypeIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_roles(current_user, ["admin"])

    ticket_type = db.query(TicketType).filter(TicketType.id == ticket_type_id).first()
    if not ticket_type:
        raise HTTPException(status_code=404, detail="Ticket type not found")

    if data.name is not None:
        ticket_type.name = data.name.strip()

    if data.price_cents is not None:
        ticket_type.price_cents = data.price_cents

    if data.currency is not None:
        ticket_type.currency = data.currency.upper().strip()

    if data.is_active is not None:
        ticket_type.is_active = bool(data.is_active)

    db.commit()

    return {
        "ok": True,
        "id": ticket_type.id,
        "event_id": ticket_type.event_id,
        "name": ticket_type.name,
        "price_cents": ticket_type.price_cents,
        "currency": ticket_type.currency,
        "is_active": getattr(ticket_type, "is_active", True),
    }

@router.post("/create_staff_test")
def create_staff_test(
    data: CreateStaffIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # dev-only endpoint — keep admin protected
    require_roles(current_user, ["admin"])

    role = data.role.lower().strip()
    if role not in {"staff", "checkin", "admin"}:
        raise HTTPException(status_code=400, detail="role must be staff, checkin, or admin")

    email = data.email.lower()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        existing.role = role
        existing.is_active = True
        if data.display_name:
            existing.display_name = data.display_name
        db.commit()
        return {
            "ok": True,
            "user_id": existing.id,
            "email": existing.email,
            "role": existing.role,
            "updated": True,
        }

    user = User(
        id=str(uuid.uuid4()),
        email=email,
        display_name=data.display_name,
        password_hash=hash_password(data.password),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    return {"ok": True, "user_id": user.id, "email": user.email, "role": user.role, "created": True}

@router.get("/live_feed")
def live_feed(
    limit: int = 20,
    event_id: str = "lfc-2027",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_roles(current_user, ["admin"])

    rows = (
        db.query(CheckIn, Ticket, User, TicketType)
        .select_from(CheckIn)
        .join(Ticket, Ticket.id == CheckIn.ticket_id)
        .join(User, User.id == Ticket.user_id)
        .join(TicketType, TicketType.id == Ticket.ticket_type_id)
        .filter(Ticket.event_id == event_id)
        .order_by(CheckIn.created_at.desc(), CheckIn.id.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "time": ci.created_at.isoformat() if ci.created_at else None,
            "email": u.email,
            "display_name": getattr(u, "display_name", ""),
            "tier": tt.name,
            "ticket_id": t.id,
        }
        for ci, t, u, tt in rows
    ]
@router.get("/lane_analytics")
def lane_analytics(
    event_id: str = "lfc-2027",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_roles(current_user, ["admin"])

    now = datetime.utcnow()
    last_5 = now - timedelta(minutes=5)
    last_60 = now - timedelta(minutes=60)

    base = (
        db.query(CheckIn)
        .join(Ticket, Ticket.id == CheckIn.ticket_id)
        .filter(Ticket.event_id == event_id)
    )

    total = base.count()

    last_5_count = (
        db.query(CheckIn)
        .join(Ticket, Ticket.id == CheckIn.ticket_id)
        .filter(Ticket.event_id == event_id)
        .filter(CheckIn.created_at >= last_5)
        .count()
    )

    last_60_count = (
        db.query(CheckIn)
        .join(Ticket, Ticket.id == CheckIn.ticket_id)
        .filter(Ticket.event_id == event_id)
        .filter(CheckIn.created_at >= last_60)
        .count()
    )

    lanes = (
        db.query(
            CheckIn.lane,
            func.count(CheckIn.id).label("count"),
        )
        .join(Ticket, Ticket.id == CheckIn.ticket_id)
        .filter(Ticket.event_id == event_id)
        .group_by(CheckIn.lane)
        .order_by(func.count(CheckIn.id).desc())
        .all()
    )

    return {
        "event_id": event_id,
        "total_checkins": total,
        "last_5_min": last_5_count,
        "last_60_min": last_60_count,
        "lanes": [
            {
                "lane": lane or "main",
                "count": count,
            }
            for lane, count in lanes
        ],
    }
@router.get("/db/table")
def db_table(
    table: str,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_roles(current_user, ["admin"])

    allowed = {
        "users": User,
        "tickets": Ticket,
        "checkins": CheckIn,
        "ticket_types": TicketType,
        "applications": Application,
    }

    model = allowed.get(table)
    if not model:
        raise HTTPException(status_code=400, detail="invalid table")

    rows = db.query(model).limit(limit).all()

    result = []
    for r in rows:
        row = {}
        for c in r.__table__.columns:
            v = getattr(r, c.name)
            row[c.name] = str(v) if v is not None else None
        result.append(row)

    return {
        "table": table,
        "count": len(result),
        "rows": result
    }
@router.get("/arrival_surge")
def arrival_surge(
    event_id: str = "lfc-2027",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_roles(current_user, ["admin"])

    now = datetime.utcnow()
    last_1 = now - timedelta(minutes=1)
    last_5 = now - timedelta(minutes=5)

    q = (
        db.query(CheckIn)
        .join(Ticket, Ticket.id == CheckIn.ticket_id)
        .filter(Ticket.event_id == event_id)
    )

    last_minute = q.filter(CheckIn.created_at >= last_1).count()
    last_5_min = q.filter(CheckIn.created_at >= last_5).count()

    avg_per_min = last_5_min / 5 if last_5_min else 0

    surge = last_minute > (avg_per_min * 2) and last_minute >= 10

    return {
        "event_id": event_id,
        "last_minute": last_minute,
        "avg_per_min": round(avg_per_min, 2),
        "surge": surge
    }

@router.get("/applications")
def admin_list_applications(
    status: str | None = None,
    application_type: str | None = None,
    event_id: str | None = None,
    reviewed: bool | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_roles(current_user, APPLICATION_REVIEW_ROLES)

    Reviewer = aliased(User)

    query = (
        db.query(Application, Reviewer)
        .outerjoin(Reviewer, Reviewer.id == Application.reviewed_by)
    )

    if status:
        if status not in APPLICATION_STATUSES:
            raise HTTPException(status_code=400, detail="Invalid status")
        query = query.filter(Application.status == status)

    if application_type:
        query = query.filter(Application.application_type == application_type)

    if event_id:
        query = query.filter(Application.event_id == event_id)

    if reviewed is True:
        query = query.filter(Application.reviewed_at.isnot(None))

    if reviewed is False:
        query = query.filter(Application.reviewed_at.is_(None))

    total = query.count()

    rows = (
        query
        .order_by(Application.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "ok": True,
        "count": len(rows),
        "total": total,
        "filters": {
            "status": status,
            "application_type": application_type,
            "event_id": event_id,
            "reviewed": reviewed,
            "limit": limit,
            "offset": offset,
        },
        "applications": [
            {
                "id": str(app.id),
                "event_id": app.event_id,
                "user_id": app.user_id,
                "application_type": app.application_type,
                "status": app.status,
                "data_json": app.data_json,
                "created_at": app.created_at,
                "updated_at": app.updated_at,
                "reviewed_by": app.reviewed_by,
                "reviewed_at": app.reviewed_at,
                "review_notes": app.review_notes,
                "reviewer_email": reviewer.email if reviewer else None,
                "reviewer_display_name": reviewer.display_name if reviewer else None,
            }
            for app, reviewer in rows
        ],
    }

@router.get("/applications/{application_id}")
def admin_get_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_roles(current_user, APPLICATION_REVIEW_ROLES)

    Reviewer = aliased(User)

    row = (
        db.query(Application, Reviewer)
        .outerjoin(Reviewer, Reviewer.id == Application.reviewed_by)
        .filter(Application.id == application_id)
        .first()
    )

    if not row:
        raise HTTPException(status_code=404, detail="Application not found")

    app, reviewer = row

    return {
        "ok": True,
        "application": {
            "id": str(app.id),
            "event_id": app.event_id,
            "user_id": app.user_id,
            "application_type": app.application_type,
            "status": app.status,
            "data_json": app.data_json,
            "created_at": app.created_at,
            "updated_at": app.updated_at,
            "reviewed_by": app.reviewed_by,
            "reviewed_at": app.reviewed_at,
            "review_notes": app.review_notes,
            "reviewer_email": reviewer.email if reviewer else None,
            "reviewer_display_name": reviewer.display_name if reviewer else None,
        },
    }

@router.patch("/applications/{application_id}/status")
def admin_update_application_status(
    application_id: str,
    payload: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_roles(current_user, APPLICATION_REVIEW_ROLES)

    if payload.status not in APPLICATION_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")

    row = db.query(Application).filter(Application.id == application_id).first()

    if not row:
        raise HTTPException(status_code=404, detail="Application not found")

    row.status = payload.status
    row.reviewed_by = current_user.id
    row.reviewed_at = datetime.utcnow()
    row.review_notes = payload.review_notes
    row.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(row)

    return {
        "ok": True,
        "application_id": str(row.id),
        "status": row.status,
        "reviewed_by": row.reviewed_by,
        "reviewed_at": row.reviewed_at,
        "review_notes": row.review_notes,
        "updated_at": row.updated_at,
    }
