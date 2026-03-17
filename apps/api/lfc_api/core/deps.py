from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from lfc_api.core.config import settings
from lfc_api.db.session import get_db
from lfc_api.models.user import User


ALGORITHM = "HS256"

def get_current_user(token: str = None, db: Session = Depends(get_db)):
    from fastapi.security import OAuth2PasswordBearer
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
    resolved_token = token or oauth2_scheme.__call__()

    if not resolved_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = jwt.decode(resolved_token, settings.secret_key, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
    except JWTError:
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
