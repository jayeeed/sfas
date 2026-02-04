"""
Face embedding service supporting multiple models.
"""
import io
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Literal

import cv2
import numpy as np
import onnxruntime as ort

from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)

ModelType = Literal["mobilefacenet", "insightface", "facenet"]


class BaseFaceModel(ABC):
    """Base class for face embedding models."""
    
    def __init__(self, model_path: Path, input_size: tuple[int, int]):
        self.model_path = model_path
        self.input_size = input_size
        self._session: ort.InferenceSession | None = None
        self._loaded = False
    
    @property
    def name(self) -> str:
        """Return model name."""
        return self.__class__.__name__.replace("Model", "").lower()
    
    def load(self) -> None:
        """Load the ONNX model."""
        if self._loaded:
            return
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        
        # Use CPU for inference
        providers = ["CPUExecutionProvider"]
        
        self._session = ort.InferenceSession(
            str(self.model_path),
            providers=providers,
        )
        self._loaded = True
        logger.info(f"Loaded {self.name} model from {self.model_path}")
    
    def preprocess(self, face_image: np.ndarray) -> np.ndarray:
        """
        Preprocess face image for the model.
        
        Args:
            face_image: BGR face image
            
        Returns:
            Preprocessed image ready for inference
        """
        # Resize to model input size
        resized = cv2.resize(face_image, self.input_size)
        
        # Convert BGR to RGB
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        
        # Normalize to [-1, 1] or [0, 1] depending on model
        normalized = self._normalize(rgb)
        
        # Add batch dimension and transpose to NCHW
        # Shape: (1, 3, H, W)
        transposed = normalized.transpose(2, 0, 1)
        batched = np.expand_dims(transposed, axis=0).astype(np.float32)
        
        return batched
    
    @abstractmethod
    def _normalize(self, image: np.ndarray) -> np.ndarray:
        """Model-specific normalization."""
        pass
    
    def get_embedding(self, face_image: np.ndarray) -> np.ndarray:
        """
        Generate embedding for a face image.
        
        Args:
            face_image: BGR face image
            
        Returns:
            1D embedding vector
        """
        if not self._loaded:
            self.load()
        
        # Preprocess
        input_tensor = self.preprocess(face_image)
        
        # Get input/output names
        input_name = self._session.get_inputs()[0].name
        output_name = self._session.get_outputs()[0].name
        
        # Run inference
        outputs = self._session.run([output_name], {input_name: input_tensor})
        
        # Get embedding and normalize
        embedding = outputs[0].flatten()
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
    
    @property
    def embedding_dim(self) -> int:
        """Return embedding dimension."""
        if not self._loaded:
            self.load()
        return self._session.get_outputs()[0].shape[-1]


class MobileFaceNetModel(BaseFaceModel):
    """MobileFaceNet model for fast CPU inference."""
    
    def __init__(self):
        model_path = settings.MODELS_BASE_PATH / "mobilefacenet" / "mobilefacenet.onnx"
        super().__init__(model_path, (112, 112))
    
    def _normalize(self, image: np.ndarray) -> np.ndarray:
        """Normalize to [-1, 1]."""
        return (image.astype(np.float32) - 127.5) / 127.5


class InsightFaceModel(BaseFaceModel):
    """InsightFace ArcFace model for high accuracy."""
    
    def __init__(self):
        # Try different possible model files
        base_path = settings.MODELS_BASE_PATH / "insightface"
        possible_files = [
            base_path / "w600k_r50.onnx",
            base_path / "buffalo_l" / "w600k_r50.onnx",
            base_path / "arcface.onnx",
        ]
        
        model_path = None
        for path in possible_files:
            if path.exists():
                model_path = path
                break
        
        if model_path is None:
            model_path = possible_files[0]  # Will fail on load with helpful message
        
        super().__init__(model_path, (112, 112))
    
    def _normalize(self, image: np.ndarray) -> np.ndarray:
        """Normalize to [-1, 1]."""
        return (image.astype(np.float32) - 127.5) / 127.5


class FaceNetModel(BaseFaceModel):
    """FaceNet model."""
    
    def __init__(self):
        model_path = settings.MODELS_BASE_PATH / "facenet" / "facenet.onnx"
        super().__init__(model_path, (160, 160))
    
    def _normalize(self, image: np.ndarray) -> np.ndarray:
        """Normalize using mean and std."""
        image = image.astype(np.float32)
        mean = np.mean(image)
        std = np.std(image)
        std = max(std, 1.0 / np.sqrt(image.size))
        return (image - mean) / std


class FaceEmbeddingService:
    """
    Service for generating face embeddings using multiple models.
    """
    
    def __init__(self):
        self._models: dict[str, BaseFaceModel] = {
            "mobilefacenet": MobileFaceNetModel(),
            "insightface": InsightFaceModel(),
            "facenet": FaceNetModel(),
        }
        self._loaded_models: set[str] = set()
    
    def load_model(self, model_type: ModelType) -> None:
        """Load a specific model."""
        if model_type not in self._models:
            raise ValueError(f"Unknown model type: {model_type}")
        
        if model_type in self._loaded_models:
            return
        
        self._models[model_type].load()
        self._loaded_models.add(model_type)
    
    def load_all_models(self) -> dict[str, bool]:
        """
        Load all available models.
        
        Returns:
            Dict of model_type -> success status
        """
        results = {}
        for model_type in self._models:
            try:
                self.load_model(model_type)
                results[model_type] = True
            except FileNotFoundError as e:
                logger.warning(f"Model {model_type} not available: {e}")
                results[model_type] = False
            except Exception as e:
                logger.error(f"Failed to load model {model_type}: {e}")
                results[model_type] = False
        
        return results
    
    def get_embedding(
        self, 
        face_image: np.ndarray, 
        model_type: ModelType = "mobilefacenet"
    ) -> np.ndarray:
        """
        Generate embedding for a face image.
        
        Args:
            face_image: BGR face image
            model_type: Which model to use
            
        Returns:
            1D embedding vector, L2 normalized
        """
        if model_type not in self._models:
            raise ValueError(f"Unknown model type: {model_type}")
        
        if model_type not in self._loaded_models:
            self.load_model(model_type)
        
        return self._models[model_type].get_embedding(face_image)
    
    def get_embedding_dim(self, model_type: ModelType) -> int:
        """Get embedding dimension for a model."""
        if model_type not in self._loaded_models:
            self.load_model(model_type)
        return self._models[model_type].embedding_dim
    
    def is_model_available(self, model_type: ModelType) -> bool:
        """Check if a model file exists."""
        if model_type not in self._models:
            return False
        return self._models[model_type].model_path.exists()
    
    def get_available_models(self) -> list[str]:
        """Get list of available (loaded or loadable) models."""
        available = []
        for model_type, model in self._models.items():
            if model.model_path.exists():
                available.append(model_type)
        return available


def serialize_embedding(embedding: np.ndarray) -> bytes:
    """Serialize numpy embedding to bytes for database storage."""
    buffer = io.BytesIO()
    np.save(buffer, embedding)
    return buffer.getvalue()


def deserialize_embedding(data: bytes) -> np.ndarray:
    """Deserialize embedding from bytes."""
    buffer = io.BytesIO(data)
    return np.load(buffer)


# Global instance
face_embedding_service = FaceEmbeddingService()
