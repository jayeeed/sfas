"""
Attendance API routes.
"""
from datetime import date, timedelta, datetime, timezone
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.logging import recognition_logger
from ...core.security import get_current_user_data, require_admin
from ...db import get_db
from ...models import Attendance, Face, User, Guest
from ...services import (
    attendance_service,
    face_detector,
    face_embedding_service,
    face_matching_service,
    ModelType,
)
from ...utils import decode_base64_image

router = APIRouter(prefix="/attendance", tags=["Attendance"])


# Schemas
class AttendanceMarkRequest(BaseModel):
    """Attendance marking request."""
    image: str = Field(..., description="Base64 encoded image")
    camera_id: str = Field(default="default", description="Camera/device ID")
    model: Literal["mobilefacenet", "insightface", "facenet"] = Field(
        default="mobilefacenet",
        description="Face recognition model to use",
    )


class AttendanceMarkResponse(BaseModel):
    """Attendance marking response."""
    success: bool
    user_id: str
    user_name: str
    emp_id: str | None
    action: Literal["check_in", "check_out"]
    confidence: float
    model_used: str
    timestamp: str
    attendance_id: str


class AttendanceRecord(BaseModel):
    """Attendance record schema."""
    id: str
    user_id: str
    user_name: str
    emp_id: str | None = None
    date: str
    check_in_time: str
    check_out_time: str | None
    check_in_confidence: float
    check_out_confidence: float | None
    check_in_source: str
    check_out_source: str | None
    check_in_model: str
    check_out_model: str | None


class AttendanceListResponse(BaseModel):
    """Attendance list response."""
    items: list[AttendanceRecord]
    total: int
    limit: int
    offset: int


class AttendanceStatsResponse(BaseModel):
    """Attendance statistics response."""
    user_id: str
    date_from: str
    date_to: str
    total_days: int
    present_days: int
    absent_days: int
    attendance_rate: float
    total_hours_worked: float


class AttendanceTodayResponse(BaseModel):
    """Today's attendance status."""
    is_checked_in: bool
    check_in_time: str | None
    check_out_time: str | None
    working_hours: float


# Routes
@router.get("/today", response_model=AttendanceTodayResponse)
async def get_today_status(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user_data)],
):
    """Get today's attendance status."""
    today_att = await attendance_service.get_today_attendance(
        db, current_user["user_id"]
    )
    
    if not today_att:
        return AttendanceTodayResponse(
            is_checked_in=False,
            check_in_time=None,
            check_out_time=None,
            working_hours=0.0,
        )
        
    working_hours = 0.0
    if today_att.check_out_time and today_att.check_in_time:
        duration = today_att.check_out_time - today_att.check_in_time
        working_hours = duration.total_seconds() / 3600
        
    return AttendanceTodayResponse(
        is_checked_in=True,
        check_in_time=today_att.check_in_time.isoformat(),
        check_out_time=today_att.check_out_time.isoformat() if today_att.check_out_time else None,
        working_hours=round(working_hours, 2),
    )


@router.post("/mark", response_model=AttendanceMarkResponse)
async def mark_attendance(
    request: AttendanceMarkRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(require_admin)],
):
    """
    Mark attendance using face recognition.
    
    - Restricted to Admins (Kiosk mode)
    - Detects face in the image
    - Matches against registered faces using the selected model
    - Creates check-in or check-out record
    """
    # Decode image
    try:
        image = decode_base64_image(request.image)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    # Detect face
    try:
        detection = face_detector.detect_single(image)
    except ValueError as e:
        recognition_logger.log_attempt(
            success=False,
            confidence=0.0,
            model_used=request.model,
            camera_id=request.camera_id,
            error=str(e),
        )
        
        # Return success=False to match frontend expectations without error toast
        now = datetime.now(timezone.utc)
        return AttendanceMarkResponse(
            success=False,
            user_id="no_face",
            user_name="No Face Detected",
            emp_id=None,
            action="check_in",
            confidence=0.0,
            model_used=request.model,
            timestamp=now.isoformat(),
            attendance_id="none",
        )
    
    # Check if model is available
    if not face_embedding_service.is_model_available(request.model):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model '{request.model}' is not available",
        )
    
    # Generate embedding
    try:
        query_embedding = face_embedding_service.get_embedding(
            detection.face_image,
            model_type=request.model,
        )
    except Exception as e:
        recognition_logger.log_attempt(
            success=False,
            confidence=0.0,
            model_used=request.model,
            camera_id=request.camera_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate embedding: {e}",
        )
    
    # Get all stored embeddings for the selected model
    result = await db.execute(
        select(Face.user_id, Face.id, Face.embedding, Face.emp_id, Face.name).where(
            Face.model_type == request.model
        )
    )
    rows = result.all()
    stored_faces = [(row.user_id, row.id, row.embedding) for row in rows]
    # Map face_id to details
    face_details_map = {row.id: {"emp_id": row.emp_id, "name": row.name} for row in rows}
    
    if not stored_faces:
        recognition_logger.log_attempt(
            success=False,
            confidence=0.0,
            model_used=request.model,
            camera_id=request.camera_id,
            error="No registered faces for this model",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No faces registered with model '{request.model}'",
        )
    
    # Find best match
    match = face_matching_service.find_best_match(
        query_embedding,
        stored_faces,
        request.model,
    )
    
    if not match:
        recognition_logger.log_attempt(
            success=False,
            confidence=0.0,
            model_used=request.model,
            camera_id=request.camera_id,
            error="No matching face found",
        )
        # Create Guest entry for unknown visitor
        
        now = datetime.now(timezone.utc)
        guest = Guest(visit_time=now)
        db.add(guest)
        await db.commit()
        await db.refresh(guest)
        
        return AttendanceMarkResponse(
            success=False,
            user_id="unknown",
            user_name="Unknown",
            emp_id=None,
            action="check_in", # Default action for unknown
            confidence=0.0,
            model_used=request.model,
            timestamp=now.isoformat(),
            attendance_id=guest.id, # Use guest ID as reference
        )
    
    # Get user info
    user_result = await db.execute(select(User).where(User.id == match.user_id))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    
    # Sort out display names
    face_details = face_details_map.get(match.face_id, {})
    caught_emp_id = face_details.get("emp_id")
    # Face name or fallback to user name if face has no name
    caught_name = face_details.get("name") or user.name

    # Mark attendance
    try:
        attendance, action = await attendance_service.mark_attendance(
            db=db,
            user_id=user.id,
            confidence=match.similarity,
            source=request.camera_id,
            model_type=request.model,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    
    # Sort out display names
    face_details = face_details_map.get(match.face_id, {})
    caught_emp_id = face_details.get("emp_id")
    # Face name or fallback to user name if face has no name
    caught_name = face_details.get("name") or user.name

    recognition_logger.log_attempt(
        success=True,
        confidence=match.similarity,
        model_used=request.model,
        camera_id=request.camera_id,
        user_id=user.id,
        action=action,
    )
    
    timestamp = (
        attendance.check_out_time if action == "check_out" else attendance.check_in_time
    )
    
    return AttendanceMarkResponse(
        success=True,
        user_id=user.id,
        user_name=caught_name or user.name, # Use variable or fallback
        emp_id=caught_emp_id,
        action=action,
        confidence=round(match.similarity, 4),
        model_used=request.model,
        timestamp=timestamp.isoformat(),
        attendance_id=attendance.id,
    )


@router.get("", response_model=AttendanceListResponse)
async def list_attendance(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user_data)],
    user_id: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """
    List attendance records.
    
    - Regular users can only view their own attendance
    - Admins can view all attendance records
    """
    # Regular users can only view their own
    if current_user["role"] != "admin":
        user_id = current_user["user_id"]
    
    attendances = await attendance_service.get_attendance_list(
        db=db,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )
    
    # Get user names and emp_ids (re-implementing dynamic fetch since migration was reverted)
    user_ids = list(set(a.user_id for a in attendances))
    user_names = {}
    user_emp_ids = {}
    user_face_names = {}
    
    if user_ids:
        # Fetch names from User table for fallback
        users_result = await db.execute(
            select(User.id, User.name).where(User.id.in_(user_ids))
        )
        user_names = {row[0]: row[1] for row in users_result.all()}
        
        # Fetch emp_ids and Face Names from Face table
        # Note: If a user has multiple faces, this might be ambiguous, 
        # but typically they belong to the same person.
        faces_result = await db.execute(
            select(Face.user_id, Face.name, Face.emp_id).where(
                Face.user_id.in_(user_ids)
            )
        )
        
        for row in faces_result.all():
            # Store the first found face name/emp_id for the user
            if row.user_id not in user_face_names and row.name:
                user_face_names[row.user_id] = row.name
            if row.user_id not in user_emp_ids and row.emp_id:
                user_emp_ids[row.user_id] = row.emp_id

    return AttendanceListResponse(
        items=[
            AttendanceRecord(
                id=a.id,
                user_id=a.user_id,
                # Prefer Face Name -> User Name -> "Unknown"
                user_name=user_face_names.get(a.user_id) or user_names.get(a.user_id, "Unknown"),
                emp_id=user_emp_ids.get(a.user_id),
                date=a.attendance_date.isoformat(),
                check_in_time=a.check_in_time.isoformat(),
                check_out_time=a.check_out_time.isoformat() if a.check_out_time else None,
                check_in_confidence=a.check_in_confidence,
                check_out_confidence=a.check_out_confidence,
                check_in_source=a.check_in_source,
                check_out_source=a.check_out_source,
                check_in_model=a.check_in_model,
                check_out_model=a.check_out_model,
            )
            for a in attendances
        ],
        total=len(attendances),
        limit=limit,
        offset=offset,
    )


@router.get("/stats/{user_id}", response_model=AttendanceStatsResponse)
async def get_attendance_stats(
    user_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user_data)],
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
):
    """Get attendance statistics for a user."""
    # Handle "me" alias
    if user_id == "me":
        user_id = current_user["user_id"]
        
    # Set default dates if not provided
    if not date_to:
        date_to = date.today()
    if not date_from:
        # Default to 30 days ago
        date_from = date_to - timedelta(days=30)

    # Regular users can only view their own stats
    if (
        current_user["user_id"] != user_id
        and current_user["role"] != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view stats for this user",
        )
    
    stats = await attendance_service.get_attendance_stats(
        db=db,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
    )
    
    return AttendanceStatsResponse(**stats)


@router.get("/{attendance_id}", response_model=AttendanceRecord)
async def get_attendance(
    attendance_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user_data)],
):
    """Get a specific attendance record."""
    result = await db.execute(
        select(Attendance).where(Attendance.id == attendance_id)
    )
    attendance = result.scalar_one_or_none()
    
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found",
        )
    
    # Check access
    if (
        current_user["user_id"] != attendance.user_id
        and current_user["role"] != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this record",
        )
    
    # Get user name
    user_result = await db.execute(
        select(User.name).where(User.id == attendance.user_id)
    )
    user_name = user_result.scalar_one_or_none() or "Unknown"
    
    return AttendanceRecord(
        id=attendance.id,
        user_id=attendance.user_id,
        user_name=user_name,
        date=attendance.attendance_date.isoformat(),
        check_in_time=attendance.check_in_time.isoformat(),
        check_out_time=attendance.check_out_time.isoformat() if attendance.check_out_time else None,
        check_in_confidence=attendance.check_in_confidence,
        check_out_confidence=attendance.check_out_confidence,
        check_in_source=attendance.check_in_source,
        check_out_source=attendance.check_out_source,
        check_in_model=attendance.check_in_model,
        check_out_model=attendance.check_out_model,
    )
class SystemOverviewResponse(BaseModel):
    """System-wide attendance overview."""
    total_employees: int
    present_today: int
    absent_today: int
    on_time_today: int
    late_today: int
    average_check_in_time: str | None


@router.get("/stats/overview", response_model=SystemOverviewResponse)
async def get_system_overview(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(require_admin)],
):
    """
    Get system-wide attendance overview for today (Admin only).
    """
    from ...utils.time_utils import get_current_time_bd
    today = get_current_time_bd().date()
    
    stats = await attendance_service.get_system_stats(
        db=db,
        date=today,
    )
    
    return SystemOverviewResponse(**stats)
