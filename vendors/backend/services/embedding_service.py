import requests
import numpy as np
import logging
from typing import List
from app.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    [The Semantic Eye]
    Converts text into mathematical vectors for meaning-based search.
    """
    
    @classmethod
    def get_embedding(cls, text: str) -> List[float]:
        """
        Calls local Ollama to get the vector for a string.
        """
        payload = {
            "model": settings.EMBEDDING_MODEL,
            "prompt": text
        }
        try:
            # Note: The Ollama embedding endpoint is /api/embeddings or /api/embed
            # Check config: it says http://localhost:11434/api/embeddings
            response = requests.post(settings.OLLAMA_API_URL, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json()["embedding"]
            else:
                logger.error(f"Embedding failed: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Embedding error: {str(e)}")
            return []

    @classmethod
    def cosine_similarity(cls, vec_a: List[float], vec_b: List[float]) -> float:
        """
        Calculates how similar two vectors are (0.0 to 1.0).
        """
        if not vec_a or not vec_b:
            return 0.0
        
        a = np.array(vec_a)
        b = np.array(vec_b)
        
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
            
        return float(dot_product / (norm_a * norm_b))
