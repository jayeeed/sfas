"""
Attendance service for managing check-in/check-out logic.
"""
from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.logging import get_logger, recognition_logger
from ..models import Attendance, User
from .face_embedding import ModelType
from ..utils.time_utils import get_current_time_bd

logger = get_logger(__name__)


class AttendanceService:
    """
    Service for managing attendance records.
    """
    
    async def get_today_attendance(
        self,
        db: AsyncSession,
        user_id: str,
    ) -> Attendance | None:
        """Get today's attendance record for a user."""
        today = get_current_time_bd().date()
        
        result = await db.execute(
            select(Attendance).where(
                Attendance.user_id == user_id,
                Attendance.attendance_date == today,
            )
        )
        return result.scalar_one_or_none()
    
    async def mark_attendance(
        self,
        db: AsyncSession,
        user_id: str,
        confidence: float,
        source: str,
        model_type: ModelType,
    ) -> tuple[Attendance, str]:
        """
        Mark attendance for a user.
        
        Args:
            db: Database session
            user_id: User ID
            confidence: Recognition confidence score
            source: Camera/device ID
            model_type: Model used for recognition
            
        Returns:
            Tuple of (attendance record, action: "check_in" or "check_out")
        """
        now = datetime.now(timezone.utc)
        today = get_current_time_bd().date()
        
        # Get user details for logging
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        user_name = user.name if user else "Unknown"
        
        # Check if there's an existing attendance record for today
        existing = await self.get_today_attendance(db, user_id)
        
        if existing is None:
            # Create new check-in record
            attendance = Attendance(
                user_id=user_id,
                attendance_date=today,
                check_in_time=now,
                check_in_confidence=confidence,
                check_in_source=source,
                check_in_model=model_type,
            )
            db.add(attendance)
            action = "check_in"
            
            logger.info(f"User {user_name} ({user_id}) checked in at {now}")
            
        else:
            # Update check-out (Continuous Check-out Logic)
            # "Last detection of the day" - we simply update the check-out time
            # every time we see the face again after check-in.
            existing.check_out_time = now
            existing.check_out_confidence = confidence
            existing.check_out_source = source
            existing.check_out_model = model_type
            attendance = existing
            action = "check_out"
            
            logger.info(f"User {user_name} ({user_id}) updated check-out at {now}")
        
        await db.flush()
        return attendance, action
    
    async def get_attendance_list(
        self,
        db: AsyncSession,
        user_id: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Attendance]:
        """
        Get attendance records with optional filters.
        
        Args:
            db: Database session
            user_id: Filter by user ID
            date_from: Filter by start date
            date_to: Filter by end date
            limit: Maximum records to return
            offset: Pagination offset
            
        Returns:
            List of attendance records
        """
        query = select(Attendance)
        
        if user_id:
            query = query.where(Attendance.user_id == user_id)
        if date_from:
            query = query.where(Attendance.attendance_date >= date_from)
        if date_to:
            query = query.where(Attendance.attendance_date <= date_to)
        
        query = query.order_by(Attendance.attendance_date.desc(), Attendance.check_in_time.desc())
        query = query.offset(offset).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_attendance_stats(
        self,
        db: AsyncSession,
        user_id: str,
        date_from: date,
        date_to: date,
    ) -> dict:
        """
        Get attendance statistics for a user.
        
        Args:
            db: Database session
            user_id: User ID
            date_from: Start date
            date_to: End date
            
        Returns:
            Dictionary with attendance stats
        """
        attendances = await self.get_attendance_list(
            db,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
            limit=1000,
        )
        
        total_days = (date_to - date_from).days + 1
        present_days = len(attendances)
        
        # Calculate total hours worked
        total_hours = 0.0
        for att in attendances:
            if att.check_out_time and att.check_in_time:
                duration = att.check_out_time - att.check_in_time
                total_hours += duration.total_seconds() / 3600
        
        return {
            "user_id": user_id,
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "total_days": total_days,
            "present_days": present_days,
            "absent_days": total_days - present_days,
            "attendance_rate": round(present_days / total_days * 100, 2) if total_days > 0 else 0,
            "total_hours_worked": round(total_hours, 2),
        }


# Global instance
attendance_service = AttendanceService()
