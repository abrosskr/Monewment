import requests
import json
import logging
from typing import Dict, List, Optional
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

class CanonicalService:
    """
    [The Universal Translator]
    Mapping "삼겹살", "Pig meat", "Pork" -> "pork_belly"
    """
    
    # 🏦 In-memory cache for speed
    _CACHE: Dict[str, str] = {
        "삼겹살": "pork_belly",
        "돼지고기": "pork",
        "김치": "kimchi",
        "신김치": "kimchi",
        "스팸": "spam",
        "두부": "tofu",
        "대파": "scallion",
        "양파": "onion",
        "마늘": "garlic",
        "고춧가루": "chili_powder",
        "간장": "soy_sauce",
        "설탕": "sugar",
        "참기름": "sesame_oil",
        "oil": "olive_oil",
        "rice": "rice",
        "밥": "rice"
    }

    @classmethod
    def get_canonical_name(cls, name: str, ai_mapping: bool = True) -> str:
        """
        Returns standardized name. Uses Cache -> AI Semantic Match.
        """
        clean_name = name.lower().strip()
        
        # 1. Direct Hit
        if clean_name in cls._CACHE:
            return cls._CACHE[clean_name]
            
        # 2. Fuzzy/Reverse Cache (e.g. "pork belly" in cache keys)
        for key, val in cls._CACHE.items():
            if key in clean_name or clean_name in key:
                return val

        # 3. [Advanced] AI Semantic Mapping
        if not ai_mapping:
            return clean_name
            
        try:
            from app.core.fis_physics import FisPhysics
            FisPhysics._load_db()
            known_ingredients = list(FisPhysics.PHYSICS_DB.keys())
            
            # Simplified Vector Search
            target_vec = EmbeddingService.get_embedding(clean_name)
            if not target_vec:
                return clean_name
                
            best_match = clean_name
            highest_sim = 0.7 # Higher threshold for AI to avoid junk
            
            # To avoid nested API calls, we only compare against a small set of "Key Categories"
            categories = ["pork", "beef", "chicken", "fish", "vegetable", "oil", "spice"]
            
            for cat in categories:
                cat_vec = EmbeddingService.get_embedding(cat) # Still slow if not cached
                sim = EmbeddingService.cosine_similarity(target_vec, cat_vec)
                if sim > highest_sim:
                    highest_sim = sim
                    best_match = cat
            
            # Cache the AI result
            cls._CACHE[clean_name] = best_match
            return best_match
            
        except Exception:
            return clean_name
