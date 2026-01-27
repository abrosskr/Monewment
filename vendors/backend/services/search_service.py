from typing import List, Dict, Any, Optional
import json
import os
from app.config import settings
from app.services.canonical_service import CanonicalService

class SearchService:
    """
    [The Matchmaker]
    Connects User Ingredients -> Valid Recipes.
    Upgraded: Now uses Canonical Mapping (Semantic Match).
    """

    # 🏅 Priority Table (Standardized keys)
    PRIORITY_SCORES = {
        "beef": 100,
        "pork": 90,
        "chicken": 80,
        "fish": 80,
        "shrimp": 70,
        "kimchi": 60,
        "spam": 55,
        "egg": 50,
        "tofu": 40,
        "onion": 10,
        "garlic": 5,
        "salt": 1,
    }

    @classmethod
    def load_all_recipes(cls) -> List[Dict]:
        """
        Loads all JSONs from data/fis_repo.
        """
        recipes = []
        repo_path = settings.FIS_DATA_PATH
        if not os.path.exists(repo_path):
            return []
            
        # Limit to 50 for speed in dev, or use all in prod
        files = [f for f in os.listdir(repo_path) if f.endswith(".json")]
        for f in files[:50]: # Search top 50 for better balance
            try:
                with open(os.path.join(repo_path, f), "r", encoding="utf-8") as file:
                    recipes.append(json.load(file))
            except:
                continue
        return recipes

    @classmethod
    def calculate_priority(cls, ingredient_name: str) -> int:
        """
        Standardizes name first, then returns score.
        """
        canonical = CanonicalService.get_canonical_name(ingredient_name)
        for key, score in cls.PRIORITY_SCORES.items():
            if key in canonical:
                return score
        return 10

    @classmethod
    def reverse_search(cls, user_ingredients: List[str]) -> List[Dict]:
        """
        [Algorithm Steps - Upgraded]
        1. Canonicalize user ingredients (AI Enabled).
        2. Match against recipe ingredients (AI Disabled for speed).
        """
        # 1. Standardize User Input (AI ON)
        user_canonical = [CanonicalService.get_canonical_name(i, ai_mapping=True) for i in user_ingredients]
        
        all_recipes = cls.load_all_recipes()
        results = []

        # Step 1: Identify Pivot
        ranked_user = sorted(
            zip(user_ingredients, user_canonical),
            key=lambda x: cls.calculate_priority(x[0]),
            reverse=True
        )
        
        if not ranked_user:
            return []
            
        pivot_raw, pivot_can = ranked_user[0]
        
        # Step 2 & 3: Filter & Score
        for recipe in all_recipes:
            r_ingredients = recipe.get("ingredients", [])
            r_ing_can = []
            
            # Optimization: AI OFF for library scan
            if isinstance(r_ingredients, dict):
                for raw_key in r_ingredients.keys():
                    clean_name = raw_key.strip().split()[0] if raw_key.strip() else ""
                    r_ing_can.append(CanonicalService.get_canonical_name(clean_name, ai_mapping=False))
            r_ing_can = [CanonicalService.get_canonical_name(str(i), ai_mapping=False) for i in r_ingredients]
                
            match_count = 0
            has_pivot = False
            
            # Semantic Pivot Check
            if pivot_can in r_ing_can:
                has_pivot = True
            
            if not has_pivot:
                continue 
                
            # Semantic Completeness
            for u_can in user_canonical:
                if u_can in r_ing_can:
                    match_count += 1
            
            completeness = (match_count / len(r_ing_can)) * 100 if r_ing_can else 0
            
            name = recipe.get("name", "Unknown")
            if name == "Unknown" and "metadata" in recipe:
                recipe_id = recipe["metadata"].get("recipe_id", "Unknown ID")
                name = f"{recipe_id} (Based on {pivot_can})"
            
            results.append({
                "recipe_name": name,
                "pivot_used": pivot_raw,
                "completeness": round(completeness, 1),
                "missing_count": len(r_ing_can) - match_count,
                "ingredients": r_ing_can # Standardized list
            })

        results.sort(key=lambda x: x["completeness"], reverse=True)
        return results
