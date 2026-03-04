from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from lfc_api.db.session import get_db
from lfc_api.models.user import User
from lfc_api.core.security import decode_access_token


def get_current_user(
    db: Session = Depends(get_db),
    token: dict = Depends(decode_access_token),
) -> User:
    user_id = token.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    u = db.query(User).filter(User.id == user_id).first()
    if not u or not u.is_active:
        raise HTTPException(status_code=401, detail="Invalid or inactive user")

    return u


def require_roles(*roles: str):
    def guard(u: User = Depends(get_current_user)) -> User:
        if u.role not in roles:
            raise HTTPException(status_code=403, detail="Not authorized")
        return u

    return guard
