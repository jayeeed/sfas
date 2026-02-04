"""
Attendance database model.
"""
from datetime import date as date_type
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .user import User


class Attendance(Base, UUIDMixin, TimestampMixin):
    """Attendance model for storing check-in/check-out records."""
    
    __tablename__ = "attendances"
    __table_args__ = (
        # Unique constraint: one attendance record per user per date
        UniqueConstraint("user_id", "attendance_date", name="uq_user_date"),
    )
    
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Attendance date
    attendance_date: Mapped[date_type] = mapped_column(Date, nullable=False, index=True)
    
    # Check-in and check-out times
    check_in_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    check_out_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Recognition confidence score (0.0 to 1.0)
    check_in_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    check_out_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Source camera/device ID
    check_in_source: Mapped[str] = mapped_column(String(100), nullable=False)
    check_out_source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # Which model was used for recognition
    check_in_model: Mapped[str] = mapped_column(String(50), nullable=False)
    check_out_model: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="attendances")
    
    @property
    def is_checked_out(self) -> bool:
        """Check if user has checked out."""
        return self.check_out_time is not None
    
    def __repr__(self) -> str:
        return f"<Attendance(id={self.id}, user_id={self.user_id}, date={self.attendance_date}, checked_out={self.is_checked_out})>"
