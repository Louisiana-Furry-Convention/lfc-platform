import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from lfc_api.db.session import get_db
from lfc_api.models.user import User
from lfc_api.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

class SignupIn(BaseModel):
    email: EmailStr
    password: str
    display_name: str = ""

class LoginIn(BaseModel):
    email: EmailStr
    password: str

@router.post("/signup")
def signup(data: SignupIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email.lower()).first():
        raise HTTPException(status_code=409, detail="Email already exists")
    u = User(
        id=str(uuid.uuid4()),
        email=data.email.lower(),
        display_name=data.display_name,
        password_hash=hash_password(data.password),
        role="attendee",
    )
    db.add(u)
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
    return {"access_token": token, "token_type": "bearer", "role": u.role}
