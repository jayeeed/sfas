"""API routes module initialization."""
from .auth import router as auth_router
from .faces import router as faces_router
from .attendance import router as attendance_router

__all__ = [
    "auth_router",
    "users_router",
    "faces_router",
    "attendance_router",
]
