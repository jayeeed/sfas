"""API module initialization."""
from .routes import auth_router, faces_router, attendance_router

__all__ = [
    "auth_router",

    "faces_router",
    "attendance_router",
]
