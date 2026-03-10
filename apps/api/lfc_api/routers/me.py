from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from lfc_api.db.session import get_db
from lfc_api.core.deps import get_current_user
from lfc_api.models.user import User

router = APIRouter(prefix="/me", tags=["me"])

@router.get("")
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # return minimal safe identity info
    return {
        "id": current_user.id,
        "email": current_user.email,
        "display_name": getattr(current_user, "display_name", ""),
        "role": current_user.role,
        "is_active": current_user.is_active,
    }
