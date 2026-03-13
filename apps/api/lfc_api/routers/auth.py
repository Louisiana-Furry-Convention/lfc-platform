import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from lfc_api.core.deps import get_current_user
from lfc_api.core.security import hash_password, verify_password, create_access_token
from lfc_api.db.session import get_db
from lfc_api.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


class SignupIn(BaseModel):
    email: EmailStr
    password: str
    display_name: str = ""


class LoginIn(BaseModel):
    email: str
    password: str


@router.post("/signup")
def signup(data: SignupIn, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="email already registered")

    user = User(
        id=str(uuid.uuid4()),
        email=data.email.lower(),
        display_name=data.display_name,
        password_hash=hash_password(data.password),
        role="attendee",
        is_active=True,
    )

    db.add(user)
    db.commit()

    return {"ok": True}


@router.post("/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.email == data.email.lower()).first()
    if not u or not verify_password(data.password, u.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not u.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")

    token = create_access_token(subject=u.id, role=u.role)

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": u.role,
        "user": {
            "id": u.id,
            "email": u.email,
            "display_name": u.display_name,
            "role": u.role,
        },
    }


@router.get("/me")
def me(u: User = Depends(get_current_user)):
    return {
        "ok": True,
        "id": u.id,
        "email": u.email,
        "role": u.role,
        "is_active": u.is_active,
    }
