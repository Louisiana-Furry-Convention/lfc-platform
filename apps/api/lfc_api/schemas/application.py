from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ApplicationCreate(BaseModel):
    application_type: str
    payload: dict[str, Any]


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    application_type: str
    status: str
    payload: str | dict[str, Any]
    created_at: datetime
    updated_at: datetime
