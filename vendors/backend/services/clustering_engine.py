import logging
import hashlib
import numpy as np
from typing import List, Dict

logger = logging.getLogger(__name__)

class ClusteringEngine:
    """
    [Food Data Factory: Step 3]
    Semantic Categorization & Archetype Discovery.
    Groups recipes into "Menu Clusters" to find the standard ideal.
    """

    def __init__(self):
        # In production, this would load a pre-trained SBERT model
        # from sentence_transformers import SentenceTransformer
        # self.model = SentenceTransformer('all-MiniLM-L6-v2')
        pass

    def get_embedding(self, text: str) -> np.ndarray:
        """
        Creates a semantic vector for the recipe.
        Currently using a reproducible hash-based mock vector.
        """
        # Reproducible random seed based on text hash
        seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % 4294967295
        np.random.seed(seed)
        return np.random.rand(384) # 384-dim mock SBERT vector

    def find_cluster_rank(self, embedding: np.ndarray, cluster_center: np.ndarray) -> float:
        """
        Calculates how close this recipe is to the 'Ideal Center' of its menu.
        Closer to center -> High CF (Content Feature) score.
        """
        # Cosine similarity logic
        norm_a = np.linalg.norm(embedding)
        norm_b = np.linalg.norm(cluster_center)
        if norm_a == 0 or norm_b == 0: return 0.5
        
        dot = np.dot(embedding, cluster_center)
        similarity = dot / (norm_a * norm_b)
        
        # Scale to 0.0 - 1.0 (CF score)
        return float(max(0.0, similarity))

    def identify_menu_cluster(self, name: str) -> str:
        """
        Heuristic clustering for basic menu identification.
        """
        name_upper = name.upper()
        if "KIMCHI" in name_upper and "STEW" in name_upper:
            return "KIMCHI_STEW_ARCHETYPE"
        if "STEAK" in name_upper:
            return "BEEF_STEAK_ARCHETYPE"
        if "PASTA" in name_upper or "SPAGHETTI" in name_upper:
            return "PASTA_ARCHETYPE"
        
        return "GENERAL_MIXED_CONE"
