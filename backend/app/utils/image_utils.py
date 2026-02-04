"""
Image processing utilities.
"""
import base64
import io
import uuid
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


def decode_base64_image(base64_string: str) -> np.ndarray:
    """
    Decode a base64 string to OpenCV image.
    
    Args:
        base64_string: Base64 encoded image (with or without data URL prefix)
        
    Returns:
        BGR image as numpy array
        
    Raises:
        ValueError: If image cannot be decoded
    """
    # Remove data URL prefix if present
    if "," in base64_string:
        base64_string = base64_string.split(",")[1]
    
    try:
        # Decode base64
        image_bytes = base64.b64decode(base64_string)
        
        # Convert to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        
        # Decode image
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError("Failed to decode image")
        
        return image
        
    except Exception as e:
        raise ValueError(f"Invalid base64 image: {e}")


def encode_image_base64(image: np.ndarray, format: str = "jpg") -> str:
    """
    Encode OpenCV image to base64 string.
    
    Args:
        image: BGR image as numpy array
        format: Output format (jpg, png)
        
    Returns:
        Base64 encoded string
    """
    if format.lower() in ("jpg", "jpeg"):
        ext = ".jpg"
        params = [cv2.IMWRITE_JPEG_QUALITY, 90]
    else:
        ext = ".png"
        params = []
    
    _, buffer = cv2.imencode(ext, image, params)
    return base64.b64encode(buffer).decode("utf-8")


def validate_image_quality(image: np.ndarray) -> tuple[bool, list[str]]:
    """
    Validate image quality for face recognition.
    
    Args:
        image: BGR image
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    # Check image size
    height, width = image.shape[:2]
    if height < 100 or width < 100:
        issues.append(f"Image too small: {width}x{height}, minimum 100x100")
    
    # Check if image is too dark or too bright
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray)
    
    if mean_brightness < 40:
        issues.append(f"Image too dark (brightness: {mean_brightness:.1f})")
    elif mean_brightness > 220:
        issues.append(f"Image too bright (brightness: {mean_brightness:.1f})")
    
    # Check blur using Laplacian variance
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
    if blur_score < 50:
        issues.append(f"Image too blurry (sharpness: {blur_score:.1f})")
    
    return len(issues) == 0, issues


def resize_image(image: np.ndarray, max_size: int = 1024) -> np.ndarray:
    """
    Resize image if larger than max_size while maintaining aspect ratio.
    
    Args:
        image: BGR image
        max_size: Maximum dimension
        
    Returns:
        Resized image (or original if smaller)
    """
    height, width = image.shape[:2]
    
    if max(height, width) <= max_size:
        return image
    
    if width > height:
        new_width = max_size
        new_height = int(height * (max_size / width))
    else:
        new_height = max_size
        new_width = int(width * (max_size / height))
    
    return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)


def save_face_image(
    image: np.ndarray,
    user_id: str,
    face_id: str | None = None,
) -> str:
    """
    Save face image to storage.
    
    Args:
        image: BGR face image
        user_id: User ID
        face_id: Optional face ID (generated if not provided)
        
    Returns:
        Relative path to saved image
    """
    if face_id is None:
        face_id = str(uuid.uuid4())
    
    # Create user directory
    user_dir = settings.FACE_IMAGES_PATH / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    
    # Save image
    filename = f"{face_id}.jpg"
    filepath = user_dir / filename
    
    cv2.imwrite(str(filepath), image, [cv2.IMWRITE_JPEG_QUALITY, 95])
    
    # Return relative path
    return f"{user_id}/{filename}"


def load_face_image(relative_path: str) -> np.ndarray | None:
    """
    Load face image from storage.
    
    Args:
        relative_path: Relative path to image
        
    Returns:
        BGR image or None if not found
    """
    filepath = settings.FACE_IMAGES_PATH / relative_path
    
    if not filepath.exists():
        return None
    
    return cv2.imread(str(filepath))


def delete_face_image(relative_path: str) -> bool:
    """
    Delete face image from storage.
    
    Args:
        relative_path: Relative path to image
        
    Returns:
        True if deleted, False if not found
    """
    filepath = settings.FACE_IMAGES_PATH / relative_path
    
    if filepath.exists():
        filepath.unlink()
        return True
    
    return False


def align_face(
    image: np.ndarray,
    landmarks: np.ndarray | None,
    target_size: tuple[int, int] = (112, 112),
) -> np.ndarray:
    """
    Align face using landmarks.
    
    Args:
        image: BGR face image
        landmarks: 5-point landmarks (optional)
        target_size: Output size
        
    Returns:
        Aligned face image
    """
    if landmarks is None or len(landmarks) < 5:
        # No landmarks, just resize
        return cv2.resize(image, target_size)
    
    # Reference points for a frontal face
    src_pts = np.array([
        [30.2946, 51.6963],
        [65.5318, 51.5014],
        [48.0252, 71.7366],
        [33.5493, 92.3655],
        [62.7299, 92.2041],
    ], dtype=np.float32)
    
    # Scale reference points to target size
    src_pts[:, 0] *= target_size[0] / 96.0
    src_pts[:, 1] *= target_size[1] / 112.0
    
    # Estimate affine transform
    dst_pts = landmarks[:5].astype(np.float32)
    
    try:
        M = cv2.estimateAffinePartial2D(dst_pts, src_pts)[0]
        if M is not None:
            aligned = cv2.warpAffine(image, M, target_size)
            return aligned
    except Exception:
        pass
    
    # Fallback to simple resize
    return cv2.resize(image, target_size)
