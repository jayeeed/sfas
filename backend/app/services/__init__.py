"""Services module initialization."""
from .face_detection import face_detector, FaceDetector, FaceDetection
from .face_embedding import (
    face_embedding_service,
    FaceEmbeddingService,
    serialize_embedding,
    deserialize_embedding,
    ModelType,
)
from .face_matching import face_matching_service, FaceMatchingService, MatchResult
from .attendance_service import attendance_service, AttendanceService

__all__ = [
    "face_detector",
    "FaceDetector",
    "FaceDetection",
    "face_embedding_service",
    "FaceEmbeddingService",
    "serialize_embedding",
    "deserialize_embedding",
    "ModelType",
    "face_matching_service",
    "FaceMatchingService",
    "MatchResult",
    "attendance_service",
    "AttendanceService",
]
