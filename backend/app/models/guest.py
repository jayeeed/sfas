"""
Guest database model.
"""
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from ..db.base import Base, TimestampMixin, UUIDMixin

class Guest(Base, UUIDMixin, TimestampMixin):
    """Guest model for storing info about unknown/unrecognized visitors."""
    
    __tablename__ = "guests"
    
    name: Mapped[str] = mapped_column(String(255), default="Unknown", nullable=False)
    visit_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    def __repr__(self) -> str:
        return f"<Guest(id={self.id}, visit_time={self.visit_time})>"
