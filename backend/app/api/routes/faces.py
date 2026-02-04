"""
Face registration API routes.
"""
from typing import Annotated, Literal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.logging import recognition_logger
from ...core.security import get_current_user_data
from ...db import get_db
from ...models import Face, User
from ...services import (
    face_detector,
    face_embedding_service,
    serialize_embedding,
    ModelType,
)
from ...utils import decode_base64_image, validate_image_quality, save_face_image

router = APIRouter(prefix="/faces", tags=["Faces"])


# Schemas
class FaceRegisterRequest(BaseModel):
    """Face registration request."""
    user_id: str
    name: str | None = None
    emp_id: str | None = None
    image: str = Field(..., description="Base64 encoded image")
    model: Literal["mobilefacenet", "insightface", "facenet"] = Field(
        default="mobilefacenet",
        description="Face recognition model to use",
    )


class FaceResponse(BaseModel):
    """Face registration response."""
    id: str
    user_id: str
    name: str | None
    emp_id: str | None
    model_type: str
    embedding_dim: int
    image_path: str
    image_url: str | None = None
    created_at: str

    class Config:
        from_attributes = True


class FaceListResponse(BaseModel):
    """List of registered faces."""
    faces: list[FaceResponse]
    total: int


class AvailableModelsResponse(BaseModel):
    """Available face recognition models."""
    models: list[str]
    default: str


# Routes
@router.get("/models", response_model=AvailableModelsResponse)
async def get_available_models():
    """Get list of available face recognition models."""
    available = face_embedding_service.get_available_models()
    return AvailableModelsResponse(
        models=available if available else ["mobilefacenet", "insightface", "facenet"],
        default="mobilefacenet",
    )


@router.get("/me", response_model=FaceListResponse)
async def get_my_faces(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user_data)],
):
    """Get registered faces for the current user."""
    result = await db.execute(select(Face).where(Face.user_id == current_user["user_id"]))
    faces = list(result.scalars().all())
    
    return FaceListResponse(
        faces=[
            FaceResponse(
                id=f.id,
                user_id=f.user_id,
                name=f.name,
                emp_id=f.emp_id,
                model_type=f.model_type,
                embedding_dim=f.embedding_dim,
                image_path=f.image_path,
                image_url=f"/static/faces/{f.image_path}" if f.image_path else None,
                created_at=f.created_at.isoformat(),
            )
            for f in faces
        ],
        total=len(faces),
    )


@router.post("/register", response_model=FaceResponse, status_code=status.HTTP_201_CREATED)
async def register_face(
    request: FaceRegisterRequest,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user_data)],
):
    """
    Register a face for a user.
    
    - Validates exactly one face in the image
    - Generates face embedding using the selected model
    - Stores the embedding and face image
    """
    # Permission check: Users can only register for themselves, unless admin
    if (
        request.user_id != current_user["user_id"]
        and current_user["role"] != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to register faces for other users",
        )

    # Verify user exists
    result = await db.execute(select(User).where(User.id == request.user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Decode and validate image
    try:
        image = decode_base64_image(request.image)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    # Check image quality
    is_valid, issues = validate_image_quality(image)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image quality issues: {', '.join(issues)}",
        )
    
    # Detect exactly one face
    try:
        detection = face_detector.detect_single(image)
    except ValueError as e:
        recognition_logger.log_registration(
            user_id=request.user_id,
            model_used=request.model,
            success=False,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    # Check if model is available
    if not face_embedding_service.is_model_available(request.model):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model '{request.model}' is not available. Please ensure the model file is installed.",
        )
    
    # Generate embedding
    try:
        embedding = face_embedding_service.get_embedding(
            detection.face_image,
            model_type=request.model,
        )
    except Exception as e:
        recognition_logger.log_registration(
            user_id=request.user_id,
            model_used=request.model,
            success=False,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate embedding: {e}",
        )
    
    # Create face record
    face = Face(
        user_id=request.user_id,
        name=request.name,
        emp_id=request.emp_id,
        embedding=serialize_embedding(embedding),
        image_path="",  # Will be updated after saving
        model_type=request.model,
        embedding_dim=len(embedding),
    )
    db.add(face)
    await db.flush()
    
    # Save face image in background
    image_path = save_face_image(detection.face_image, request.user_id, face.id)
    face.image_path = image_path
    
    await db.flush()
    await db.refresh(face)
    
    recognition_logger.log_registration(
        user_id=request.user_id,
        model_used=request.model,
        success=True,
    )
    
    return FaceResponse(
        id=face.id,
        user_id=face.user_id,
        name=face.name,
        emp_id=face.emp_id,
        model_type=face.model_type,
        embedding_dim=face.embedding_dim,
        image_path=face.image_path,
        image_url=f"/static/faces/{face.image_path}" if face.image_path else None,
        created_at=face.created_at.isoformat(),
    )


@router.get("/{user_id}", response_model=FaceListResponse)
async def get_user_faces(
    user_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user_data)],
):
    """Get all registered faces for a user."""
    # Users can view their own faces, admins can view all
    if (
        current_user["user_id"] != user_id
        and current_user["role"] != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view faces for this user",
        )
    
    result = await db.execute(select(Face).where(Face.user_id == user_id))
    faces = list(result.scalars().all())
    
    return FaceListResponse(
        faces=[
            FaceResponse(
                id=f.id,
                user_id=f.user_id,
                name=f.name,
                emp_id=f.emp_id,
                model_type=f.model_type,
                embedding_dim=f.embedding_dim,
                image_path=f.image_path,
                image_url=f"/static/faces/{f.image_path}" if f.image_path else None,
                created_at=f.created_at.isoformat(),
            )
            for f in faces
        ],
        total=len(faces),
    )


@router.delete("/{face_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_face(
    face_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user_data)],
):
    """Delete a face registration (admin or self only)."""
    result = await db.execute(select(Face).where(Face.id == face_id))
    face = result.scalar_one_or_none()
    
    if not face:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Face not found",
        )
        
    # Check permissions (self or admin)
    if current_user["user_id"] != face.user_id and current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this face",
        )
    
    # Delete face image from storage
    from ...utils import delete_face_image
    delete_face_image(face.image_path)
    
    await db.delete(face)
    await db.flush()
