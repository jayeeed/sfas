"""
Application configuration using Pydantic Settings.
"""
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application
    APP_NAME: str = "Smart Face Attendance System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str
    
    # JWT Configuration
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Model Paths (relative to backend/models/)
    MODELS_BASE_PATH: Path = Path(__file__).parent.parent.parent / "models"
    
    # Face Detection
    FACE_DETECTION_MODEL: str = "yunet"  # or "haar", "dnn"
    FACE_DETECTION_CONFIDENCE: float = 0.7
    
    # Face Recognition Models
    DEFAULT_RECOGNITION_MODEL: Literal["mobilefacenet", "insightface", "facenet"] = "mobilefacenet"
    
    # Similarity Thresholds (per model)
    MOBILEFACENET_THRESHOLD: float = 0.65
    INSIGHTFACE_THRESHOLD: float = 0.45
    FACENET_THRESHOLD: float = 0.70
    
    # Storage
    STORAGE_PATH: Path = Path(__file__).parent.parent.parent / "storage"
    FACE_IMAGES_PATH: Path = Path(__file__).parent.parent.parent / "storage" / "face_images"
    
    # Image Processing
    MAX_IMAGE_SIZE_MB: int = 10
    MIN_FACE_SIZE: int = 80  # minimum face detection size in pixels
    
    @field_validator("DATABASE_URL")
    @classmethod
    def assemble_db_connection(cls, v: str | None) -> str:
        if not v:
            raise ValueError("DATABASE_URL must be set")
        if v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        # asyncpg connection string adjustments
        # Replace sslmode with ssl (asyncpg expects ssl)
        v = v.replace("sslmode=require", "ssl=require")
        # Remove unsupported channel_binding
        v = v.replace("channel_binding=require", "")
        # Cleanup URL parameters
        v = v.replace("&&", "&").replace("?&", "?").rstrip("&")
        
        return v
    
    @property
    def similarity_thresholds(self) -> dict[str, float]:
        """Get similarity thresholds for each model."""
        return {
            "mobilefacenet": self.MOBILEFACENET_THRESHOLD,
            "insightface": self.INSIGHTFACE_THRESHOLD,
            "facenet": self.FACENET_THRESHOLD,
        }
    
    @property
    def model_input_sizes(self) -> dict[str, tuple[int, int]]:
        """Get input image size for each model."""
        return {
            "mobilefacenet": (112, 112),
            "insightface": (112, 112),
            "facenet": (160, 160),
        }


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
