# apps/api/lfc_api/models/application.py

from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from lfc_api.models.base import Base  # adjust if needed

class Application(Base):
    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    event_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)

    application_type: Mapped[str] = mapped_column(String, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String, index=True, nullable=False)
    current_stage: Mapped[str | None] = mapped_column(String, index=True, nullable=True)

    title: Mapped[str] = mapped_column(String, nullable=False)
    target_department: Mapped[str | None] = mapped_column(String, nullable=True)
    target_role: Mapped[str | None] = mapped_column(String, nullable=True)

    data_json: Mapped[dict] = mapped_column(JSON, nullable=False)

    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    withdrawn_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user = relationship("User")
    reviews = relationship(
        "ApplicationReview",
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="ApplicationReview.created_at.desc()",
    )

    __table_args__ = (
        Index("ix_applications_event_type_status", "event_id", "application_type", "status"),
    )
