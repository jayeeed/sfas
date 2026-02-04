"""
Structured logging configuration for the application.
"""
import logging
import sys
from datetime import datetime
from typing import Any

from .config import settings


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        # Add timestamp
        record.timestamp = datetime.utcnow().isoformat()
        
        # Format message
        log_data = {
            "timestamp": record.timestamp,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields if present
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return str(log_data)


def setup_logging() -> None:
    """Configure application logging."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Use structured formatter in production, simple in debug
    if settings.DEBUG:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    else:
        formatter = StructuredFormatter()
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Reduce noise from third-party libraries
    # Keep uvicorn.access at INFO to see HTTP request logs
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)


class RecognitionLogger:
    """Specialized logger for face recognition attempts."""
    
    def __init__(self):
        self.logger = get_logger("recognition")
    
    def log_attempt(
        self,
        success: bool,
        confidence: float,
        model_used: str,
        camera_id: str | None = None,
        user_id: str | None = None,
        **extra: Any,
    ) -> None:
        """Log a face recognition attempt."""
        log_data = {
            "event": "recognition_attempt",
            "success": success,
            "confidence": confidence,
            "model_used": model_used,
            "camera_id": camera_id,
            "user_id": user_id,
            **extra,
        }
        
        if success:
            self.logger.info(f"Recognition successful: {log_data}")
        else:
            self.logger.warning(f"Recognition failed: {log_data}")
    
    def log_registration(
        self,
        user_id: str,
        model_used: str,
        success: bool = True,
        error: str | None = None,
    ) -> None:
        """Log a face registration attempt."""
        log_data = {
            "event": "face_registration",
            "user_id": user_id,
            "model_used": model_used,
            "success": success,
        }
        
        if error:
            log_data["error"] = error
            self.logger.error(f"Registration failed: {log_data}")
        else:
            self.logger.info(f"Registration successful: {log_data}")


recognition_logger = RecognitionLogger()
