"""
Face database model for storing face embeddings.
"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .user import User


class Face(Base, UUIDMixin, TimestampMixin):
    """Face model for storing face embeddings and image paths."""
    
    __tablename__ = "faces"
    
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Face label/name (e.g., "Front View")
    name: Mapped[str] = mapped_column(String(255), nullable=True)

    # Employee ID (optional metadata)
    emp_id: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
    
    
    # Embedding stored as binary (serialized NumPy array)
    embedding: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    
    # Path to stored face image
    image_path: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Which model was used to generate this embedding
    model_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    
    # Embedding dimension (for validation)
    embedding_dim: Mapped[int] = mapped_column(nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="faces")
    
    def __repr__(self) -> str:
        return f"<Face(id={self.id}, user_id={self.user_id}, model_type={self.model_type})>"
