"""
Face detection service using OpenCV DNN.
"""
import cv2
import numpy as np
from pathlib import Path
from typing import NamedTuple

from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class FaceDetection(NamedTuple):
    """Detected face result."""
    bbox: tuple[int, int, int, int]  # (x, y, width, height)
    confidence: float
    face_image: np.ndarray
    landmarks: np.ndarray | None = None


class FaceDetector:
    """
    Face detector using OpenCV's YuNet model.
    Falls back to Haar Cascade if YuNet is not available.
    """
    
    def __init__(self):
        self._detector = None
        self._haar_cascade = None
        self._initialized = False
    
    def _initialize(self) -> None:
        """Lazy initialization of the detector."""
        if self._initialized:
            return
        
        # Try to load YuNet first (better accuracy)
        yunet_path = settings.MODELS_BASE_PATH / "detection" / "face_detection_yunet_2023mar.onnx"
        
        if yunet_path.exists():
            try:
                self._detector = cv2.FaceDetectorYN.create(
                    str(yunet_path),
                    "",
                    (320, 320),
                    settings.FACE_DETECTION_CONFIDENCE,
                    0.3,  # NMS threshold
                    5000,  # top_k
                )
                logger.info("Initialized YuNet face detector")
                self._initialized = True
                return
            except Exception as e:
                logger.warning(f"Failed to load YuNet: {e}, falling back to Haar Cascade")
        
        # Fallback to Haar Cascade
        haar_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self._haar_cascade = cv2.CascadeClassifier(haar_path)
        logger.info("Initialized Haar Cascade face detector")
        self._initialized = True
    
    def detect(self, image: np.ndarray) -> list[FaceDetection]:
        """
        Detect faces in an image.
        
        Args:
            image: BGR image as numpy array
            
        Returns:
            List of FaceDetection objects
        """
        self._initialize()
        
        if self._detector is not None:
            return self._detect_yunet(image)
        else:
            return self._detect_haar(image)
    
    def _detect_yunet(self, image: np.ndarray) -> list[FaceDetection]:
        """Detect faces using YuNet."""
        height, width = image.shape[:2]
        
        # Set input size to image size
        self._detector.setInputSize((width, height))
        
        # Detect faces
        _, faces = self._detector.detect(image)
        
        if faces is None:
            return []
        
        detections = []
        for face in faces:
            x, y, w, h = int(face[0]), int(face[1]), int(face[2]), int(face[3])
            confidence = float(face[-1])
            
            # Extract landmarks (5 points: right eye, left eye, nose, right mouth, left mouth)
            landmarks = face[4:14].reshape(5, 2) if len(face) >= 14 else None
            
            # Crop face with some margin
            margin = 0.1
            x1 = max(0, int(x - w * margin))
            y1 = max(0, int(y - h * margin))
            x2 = min(width, int(x + w * (1 + margin)))
            y2 = min(height, int(y + h * (1 + margin)))
            
            face_image = image[y1:y2, x1:x2]
            
            if face_image.size > 0:
                detections.append(FaceDetection(
                    bbox=(x, y, w, h),
                    confidence=confidence,
                    face_image=face_image,
                    landmarks=landmarks,
                ))
        
        return detections
    
    def _detect_haar(self, image: np.ndarray) -> list[FaceDetection]:
        """Detect faces using Haar Cascade (fallback)."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        faces = self._haar_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(settings.MIN_FACE_SIZE, settings.MIN_FACE_SIZE),
        )
        
        detections = []
        height, width = image.shape[:2]
        
        for (x, y, w, h) in faces:
            confidence = 0.9  # Haar doesn't provide confidence
            
            # Crop face with margin
            margin = 0.1
            x1 = max(0, int(x - w * margin))
            y1 = max(0, int(y - h * margin))
            x2 = min(width, int(x + w * (1 + margin)))
            y2 = min(height, int(y + h * (1 + margin)))
            
            face_image = image[y1:y2, x1:x2]
            
            if face_image.size > 0:
                detections.append(FaceDetection(
                    bbox=(x, y, w, h),
                    confidence=confidence,
                    face_image=face_image,
                    landmarks=None,
                ))
        
        return detections
    
    def detect_single(self, image: np.ndarray) -> FaceDetection | None:
        """
        Detect exactly one face in an image.
        
        Args:
            image: BGR image as numpy array
            
        Returns:
            FaceDetection if exactly one face found, None otherwise
            
        Raises:
            ValueError: If no face or multiple faces detected
        """
        detections = self.detect(image)
        
        if len(detections) == 0:
            raise ValueError("No face detected in image")
        
        if len(detections) > 1:
            raise ValueError(f"Multiple faces detected ({len(detections)}), expected exactly one")
        
        return detections[0]


# Global instance
face_detector = FaceDetector()
