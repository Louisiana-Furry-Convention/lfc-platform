from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from lfc_api.models.base import Base

class ConventionEvent(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # e.g. lfc-2027
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped["DateTime"] = mapped_column(DateTime, server_default=func.now())
