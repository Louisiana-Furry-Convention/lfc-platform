import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import func

from lfc_api.db.session import get_db
from lfc_api.models.user import User
from lfc_api.models.ticketing import CheckIn, Ticket, TicketType

from lfc_api.core.deps import get_current_user
from lfc_api.core.authz import require_roles
from lfc_api.core.security import hash_password

router = APIRouter(prefix="/admin", tags=["admin"])


class CreateStaffIn(BaseModel):
    email: EmailStr
    display_name: str = ""
    password: str = "staffpass123"
    role: str = "staff"  # allowed: staff, checkin, admin


class PromoteIn(BaseModel):
    user_id: str
    role: str  # staff | checkin | admin
    is_active: bool = True


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
