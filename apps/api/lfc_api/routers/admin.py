import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from lfc_api.db.session import get_db
from lfc_api.models.user import User
from lfc_api.core.security import hash_password

router = APIRouter(prefix="/admin", tags=["admin"])


class CreateStaffIn(BaseModel):
    email: EmailStr
    display_name: str = ""
    password: str = "staffpass123"
    role: str = "staff"  # allowed: staff, checkin, admin

class PromoteUserIn(BaseModel):
    user_id: str
    role: str = "checkin"  # staff, checkin, admin

@router.post("/create_staff_test")
def create_staff_test(data: CreateStaffIn, db: Session = Depends(get_db)):
    role = data.role.lower().strip()
    if role not in {"staff", "checkin", "admin"}:
        raise HTTPException(status_code=400, detail="role must be staff, checkin, or admin")

    email = data.email.lower()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        # If user already exists, just upgrade role (dev-only behavior)
        existing.role = role
        if data.display_name:
            existing.display_name = data.display_name
        db.commit()
        return {"ok": True, "user_id": existing.id, "email": existing.email, "role": existing.role, "updated": True}

@router.post("/promote_user_role")
def promote_user_role(data: PromoteUserIn, db: Session = Depends(get_db)):
    role = data.role.lower().strip()
    if role not in {"staff", "checkin", "admin"}:
        raise HTTPException(status_code=400, detail="role must be staff, checkin, or admin")

    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = role
    user.is_active = True
    db.commit()

    return {"ok": True, "user_id": user.id, "email": user.email, "role": user.role}

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
