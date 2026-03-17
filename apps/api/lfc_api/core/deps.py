from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from lfc_api.core.security import decode_access_token
from lfc_api.db.session import get_db
from lfc_api.models.user import User


def get_current_user(
    payload: dict = Depends(decode_access_token),
    db: Session = Depends(get_db),
):
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


def require_roles(*allowed_roles: str) -> Callable:
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        user_role = getattr(current_user, "role", None)
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return dependency


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    user_role = getattr(current_user, "role", None)
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
