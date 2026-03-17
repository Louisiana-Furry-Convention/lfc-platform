import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func

from lfc_api.models.base import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(50), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    application_type = Column(String(30), nullable=False)
    status = Column(String(30), nullable=False, default="submitted")

    data_json = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

