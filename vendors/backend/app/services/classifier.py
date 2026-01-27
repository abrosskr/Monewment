from sqlalchemy.orm import Session
from ..models import FoodType, StandardRecipe
from .normalizer import IngredientNormalizer
import re

class FoodClassifier:
    def __init__(self, db_session: Session = None):
        self.db = db_session
        self.normalizer = IngredientNormalizer()
        
        # In-memory Rule Set (Simulation of a learned model)
        # Keyword -> FoodType Name
        self.rules = {
            "버거": "Burger",
            "피자": "Pizza",
            "찌개": "Jjigae",
            "전골": "Jjigae", # Mapping 'Jeongol' to Jjigae type for simplicity or create new
            "국수": "NoodleSoup",
            "면": "NoodleSoup",
            "라면": "NoodleSoup",
            "짬뽕": "NoodleSoup",
            "우동": "NoodleSoup",
            "덮밥": "RiceBowl",
            "비빔밥": "RiceBowl",
            "볶음밥": "RiceBowl", # Broad category
            "타코": "Taco",
            "카레": "Curry",
            "커리": "Curry",
            "초밥": "Sushi",
            "스시": "Sushi",
            "샌드위치": "Sandwich",
            "토스트": "Sandwich"
        }

    def classify_recipe(self, recipe_name: str, ingredients_list: list):
        """
        Input: 
          name: "돼지고기 김치찌개"
          ingredients: [{"item": "돼지고기", "qty": "300g"}, ...]
        
        Output:
          {
            "food_type": "Jjigae",
            "base": "Broth (Liquid)",
            "protein": "Pork",
            "confidence": "High"
          }
        """
        result = {
            "food_type": None,
            "base": None,
            "protein": None,
            "confidence": "Low",
            "method": None
        }
        
        # 1. Determine Food Type (Rule-based)
        # Scan name for keywords
        for keyword, type_name in self.rules.items():
            if keyword in recipe_name:
                result["food_type"] = type_name
                result["confidence"] = "Medium" # Keyword match
                break
        
        # If DB session is available, fetch details
        if self.db and result["food_type"]:
            ft = self.db.query(FoodType).filter_by(name=result["food_type"]).first()
            if ft:
                result["base"] = ft.base_material
                result["method"] = ft.default_method
        else:
            # Fallback hardcoded for testing without DB
            defaults = {
                "Burger": "Bread (Bun)", "Pizza": "Dough", "Jjigae": "Broth",
                "NoodleSoup": "Noodle", "RiceBowl": "Rice", "Taco": "Tortilla",
                "Curry": "Curry Sauce", "Sushi": "Rice (Vinegar)", "Sandwich": "Bread"
            }
            result["base"] = defaults.get(result["food_type"], "Unknown")

        # 2. Determine Protein (Modifier)
        # Strategy: Look at the normalized ingredients. 
        # Protein usually comes from common meats/seafoods.
        
        # Candidates for Protein
        candidates = []
        for ing in ingredients_list:
            raw_item = ing.get('item', '')
            norm_item = self.normalizer.normalize(raw_item)
            
            # Simple heuristic: If it matches known proteins
            if "Pork" in norm_item or "Beef" in norm_item or "Chicken" in norm_item or \
               "Shrimp" in norm_item or "Seafood" in norm_item or "Egg" in norm_item or \
               "Tuna" in norm_item or "Kimchi" in norm_item: # Kimchi can be main modifier
                 candidates.append(norm_item)
        
        # Also check Name for modifiers (e.g. "Bulgogi" in "Bulgogi Burger")
        name_lower = recipe_name
        
        # Heuristic: Match candidate found in ingredients that ALSO appears in Name?
        # Or just take the first major protein found in ingredients.
        
        if candidates:
            # Prioritize: If item name is in Recipe Name (e.g. "Kimchi" in "Kimchi Jjigae")
            best_match = candidates[0] 
            for c in candidates:
                # Reverse lookup? Hard because candidates are English "Pork" and name is "돼지"
                # Need Reverse Mapping or check raw ingredients again.
                pass
            
            result["protein"] = candidates[0] # Pick first for now
            if len(candidates) > 1:
                # Compound? "Kimchi + Pork"
                # Join top 2
                result["protein"] = " + ".join(candidates[:2])
        
        return result
