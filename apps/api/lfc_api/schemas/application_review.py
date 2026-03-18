# apps/api/lfc_api/schemas/application_review.py

from datetime import datetime
from pydantic import BaseModel


class ApplicationReviewCreate(BaseModel):
    stage: str
    decision: str | None = None
    notes: str | None = None


class ApplicationReviewRead(BaseModel):
    id: str
    application_id: str
    stage: str
    decision: str | None
    reviewed_by_user_id: str
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
