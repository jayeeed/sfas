"""
Smart Face Attendance System - FastAPI Application
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.logging import setup_logging, get_logger
from .db import init_db, close_db
from .api import auth_router, faces_router, attendance_router
from .services import face_embedding_service

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    setup_logging()
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Preload face recognition models
    logger.info("Loading face recognition models...")
    model_status = face_embedding_service.load_all_models()
    for model_name, loaded in model_status.items():
        if loaded:
            logger.info(f"  ✓ {model_name} loaded")
        else:
            logger.warning(f"  ✗ {model_name} not available")
    
    yield
    
    # Shutdown
    await close_db()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
Smart Face Attendance System API

## Features
- Face registration with multiple face recognition models
- Face recognition-based attendance marking
- User management with role-based access control
- JWT authentication

## Face Recognition Models
- **MobileFaceNet**: Fast, lightweight (~4MB), good for real-time
- **InsightFace (ArcFace)**: High accuracy (~250MB), best for enrollment
- **FaceNet**: Balanced accuracy and speed (~95MB)

Select the model using the `model` parameter in face registration and attendance marking endpoints.
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(faces_router, prefix=settings.API_V1_PREFIX)
app.include_router(attendance_router, prefix=settings.API_V1_PREFIX)

# Mount static files
from fastapi.staticfiles import StaticFiles
import os
os.makedirs(settings.FACE_IMAGES_PATH, exist_ok=True)
app.mount("/static/faces", StaticFiles(directory=settings.FACE_IMAGES_PATH), name="static_faces")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    available_models = face_embedding_service.get_available_models()
    
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "models": {
            "available": available_models,
            "default": settings.DEFAULT_RECOGNITION_MODEL,
        },
    }
