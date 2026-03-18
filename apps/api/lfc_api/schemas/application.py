# apps/api/lfc_api/schemas/application.py

from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from lfc_api.core.application_constants import (
    APPLICATION_STATUS_DRAFT,
    APPLICATION_STATUS_SUBMITTED,
    is_valid_application_type,
)


class ApplicationCreate(BaseModel):
    event_id: str
    application_type: str
    status: str = APPLICATION_STATUS_SUBMITTED
    title: str = Field(min_length=1)
    target_department: str | None = None
    target_role: str | None = None
    data_json: dict

    @field_validator("application_type")
    @classmethod
    def validate_application_type(cls, value: str) -> str:
        if not is_valid_application_type(value):
            raise ValueError("invalid application_type")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        if value not in {APPLICATION_STATUS_DRAFT, APPLICATION_STATUS_SUBMITTED}:
            raise ValueError("status must be draft or submitted")
        return value


class ApplicationListItem(BaseModel):
    id: str
    event_id: str
    application_type: str
    status: str
    current_stage: str | None
    title: str
    submitted_at: datetime | None
    updated_at: datetime

    model_config = {"from_attributes": True}


class ApplicationRead(BaseModel):
    id: str
    event_id: str
    user_id: str
    application_type: str
    status: str
    current_stage: str | None
    title: str
    target_department: str | None
    target_role: str | None
    data_json: dict
    submitted_at: datetime | None
    withdrawn_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ApplicationWithdrawResponse(BaseModel):
    ok: bool
    application_id: str
    status: str
    withdrawn_at: datetime


class ApplicationStatusUpdate(BaseModel):
    status: str


class ApplicationStageUpdate(BaseModel):
    current_stage: str
