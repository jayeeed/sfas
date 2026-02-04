"""
Face matching service for comparing embeddings.
"""
from typing import NamedTuple

import numpy as np
from scipy.spatial.distance import cosine

from ..core.config import settings
from ..core.logging import get_logger
from .face_embedding import deserialize_embedding, ModelType

logger = get_logger(__name__)


class MatchResult(NamedTuple):
    """Face match result."""
    user_id: str
    similarity: float
    is_match: bool
    face_id: str


class FaceMatchingService:
    """
    Service for matching face embeddings.
    """
    
    def __init__(self):
        # In-memory cache for embeddings per model
        self._embedding_cache: dict[str, dict[str, list[tuple[str, np.ndarray]]]] = {
            "mobilefacenet": {},
            "insightface": {},
            "facenet": {},
        }
        self._cache_loaded = False
    
    def cosine_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding (L2 normalized)
            embedding2: Second embedding (L2 normalized)
            
        Returns:
            Similarity score (0 to 1, higher is more similar)
        """
        # Cosine distance is 1 - cosine_similarity for normalized vectors
        # Since embeddings are L2 normalized, we can use dot product
        return float(np.dot(embedding1, embedding2))
    
    def find_best_match(
        self,
        query_embedding: np.ndarray,
        stored_embeddings: list[tuple[str, str, bytes]],  # (user_id, face_id, embedding_bytes)
        model_type: ModelType,
    ) -> MatchResult | None:
        """
        Find the best matching face from stored embeddings.
        
        Args:
            query_embedding: Embedding of the query face
            stored_embeddings: List of (user_id, face_id, embedding_bytes) tuples
            model_type: Model type used for embeddings
            
        Returns:
            Best match result if above threshold, None otherwise
        """
        if not stored_embeddings:
            return None
        
        threshold = settings.similarity_thresholds.get(model_type, 0.65)
        
        best_match: MatchResult | None = None
        best_similarity = -1.0
        
        for user_id, face_id, embedding_bytes in stored_embeddings:
            stored_embedding = deserialize_embedding(embedding_bytes)
            similarity = self.cosine_similarity(query_embedding, stored_embedding)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = MatchResult(
                    user_id=user_id,
                    similarity=similarity,
                    is_match=similarity >= threshold,
                    face_id=face_id,
                )
        
        # Only return if it's actually a match
        if best_match and best_match.is_match:
            return best_match
        
        return None
    
    def find_all_matches(
        self,
        query_embedding: np.ndarray,
        stored_embeddings: list[tuple[str, str, bytes]],
        model_type: ModelType,
        top_k: int = 5,
    ) -> list[MatchResult]:
        """
        Find top-k matching faces from stored embeddings.
        
        Args:
            query_embedding: Embedding of the query face
            stored_embeddings: List of (user_id, face_id, embedding_bytes) tuples
            model_type: Model type used for embeddings
            top_k: Number of top matches to return
            
        Returns:
            List of match results sorted by similarity (descending)
        """
        if not stored_embeddings:
            return []
        
        threshold = settings.similarity_thresholds.get(model_type, 0.65)
        
        matches = []
        for user_id, face_id, embedding_bytes in stored_embeddings:
            stored_embedding = deserialize_embedding(embedding_bytes)
            similarity = self.cosine_similarity(query_embedding, stored_embedding)
            
            matches.append(MatchResult(
                user_id=user_id,
                similarity=similarity,
                is_match=similarity >= threshold,
                face_id=face_id,
            ))
        
        # Sort by similarity descending
        matches.sort(key=lambda x: x.similarity, reverse=True)
        
        return matches[:top_k]
    
    def batch_compare(
        self,
        query_embedding: np.ndarray,
        embeddings_matrix: np.ndarray,
    ) -> np.ndarray:
        """
        Efficiently compare query against multiple embeddings using matrix operations.
        
        Args:
            query_embedding: Query embedding (1D array)
            embeddings_matrix: Matrix of embeddings (N x D)
            
        Returns:
            Array of similarity scores
        """
        # Dot product for L2 normalized vectors = cosine similarity
        similarities = embeddings_matrix @ query_embedding
        return similarities
    
    def verify_faces(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray,
        model_type: ModelType,
    ) -> tuple[bool, float]:
        """
        Verify if two face embeddings belong to the same person.
        
        Args:
            embedding1: First face embedding
            embedding2: Second face embedding
            model_type: Model type used for embeddings
            
        Returns:
            Tuple of (is_same_person, similarity_score)
        """
        threshold = settings.similarity_thresholds.get(model_type, 0.65)
        similarity = self.cosine_similarity(embedding1, embedding2)
        
        return similarity >= threshold, similarity


# Global instance
face_matching_service = FaceMatchingService()
