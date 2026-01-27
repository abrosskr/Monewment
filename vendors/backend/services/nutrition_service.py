from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.engines.product_standard.interface import ProductStandardInterface
from app.engines.product_standard.models import ProductMaster
from app.engines.product_standard.parser import ProductDataParser, WeightUnit

class NutritionService:
    """
    [Precision Calculator]
    Maps recipe ingredients to ProductMaster items and calculates total calories.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.product_api = ProductStandardInterface(db)

    def calculate_recipe_nutrition(self, ingredients: List[str]) -> Dict[str, Any]:
        """
        Input: ["Spaghetti 200g", "Olive Oil 20ml", "Garlic 10g"]
        Output: Total Calories + Breakdown
        """
        total_calories = 0
        breakdown = []
        
        for ing in ingredients:
            # 1. Parse Input Amount (Simple Heuristic for Prototype)
            # "Spaghetti 200g" -> val=200, unit=g, query="Spaghetti"
            parsed_val, parsed_unit = ProductDataParser.parse_weight(ing)
            
            # Use Regex to remove the weight part (e.g. "200g", "200 g", "200ml")
            import re
            # Remove specs like 200g, 200 ml, 1kg
            query = re.sub(r'[0-9.]+\s*(g|kg|ml|l|oz|lb)s?', '', ing, flags=re.IGNORECASE).strip()
            # Also clean up extra spaces or punctuation
            query = re.sub(r'\s+', ' ', query).strip()
            
            # 2. Match Product
            # Priority: Try to find a match in our Seeded DB
            products = self.product_api.search_by_name(query)
            
            matched_product = None
            if products:
                # Pick best match (First for now)
                matched_product = products[0]
            
            # 3. Calculate
            if matched_product and matched_product.nutrition_json:
                # DEBUG
                # print(f"[Debug] Found: {matched_product.product_name}, Nutrition Type: {type(matched_product.nutrition_json)}")
                
                nutri_data = matched_product.nutrition_json
                # Handle case if it's a string (SQLite artifact)
                if isinstance(nutri_data, str):
                    import json
                    try:
                        nutri_data = json.loads(nutri_data)
                    except:
                        nutri_data = {}

                kcal_per_100 = nutri_data.get("kcal", 0)
                
                # Normalize calculation to Grams
                amount_in_g = parsed_val # Parser returns g/ml standard
                
                # Calorie Math: (Kcal / 100) * amount
                item_calories = (kcal_per_100 / 100.0) * amount_in_g
                total_calories += item_calories
                
                breakdown.append({
                    "ingredient": ing,
                    "matched_product": f"[{matched_product.brand}] {matched_product.product_name}",
                    "amount_g": amount_in_g,
                    "calories": round(item_calories, 1)
                })
            else:
                breakdown.append({
                    "ingredient": ing,
                    "matched_product": "Unknown",
                    "calories": 0
                })
                
        return {
            "total_calories": round(total_calories),
            "breakdown": breakdown
        }
