# apps/api/lfc_api/models/application_review.py

from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lfc_api.models.base import Base  # adjust if needed


class ApplicationReview(Base):
    __tablename__ = "application_reviews"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    application_id: Mapped[str] = mapped_column(
        ForeignKey("applications.id"),
        index=True,
        nullable=False,
    )
    stage: Mapped[str] = mapped_column(String, index=True, nullable=False)
    decision: Mapped[str | None] = mapped_column(String, nullable=True)
    reviewed_by_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    application = relationship("Application", back_populates="reviews")
    reviewed_by = relationship("User")

    __table_args__ = (
        Index("ix_application_reviews_application_stage", "application_id", "stage"),
    )

