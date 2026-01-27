import os
import requests
import time
from typing import Optional, Dict
from app.models.matter import IngredientModel, FlavorProfile, PhysicalProperties, ReactionPotential

class USDAScraper:
    """
    Connects to USDA FoodData Central API to populate MatterDB.
    """
    BASE_URL = "https://api.nal.usda.gov/fdc/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("USDA_API_KEY")
        
    def search_food(self, query: str) -> Optional[Dict]:
        """
        Search for a food item by name.
        """
        if not self.api_key:
            print("⚠️ USDA API Key missing.")
            return None
            
        endpoint = f"{self.BASE_URL}/foods/search"
        params = {
            "api_key": self.api_key,
            "query": query,
            "dataType": ["Foundation", "SR Legacy"],
            "pageSize": 1
        }
        try:
            resp = requests.get(endpoint, params=params)
            resp.raise_for_status()
            data = resp.json()
            if data["foods"]:
                return data["foods"][0]
        except Exception as e:
            print(f"Error searching USDA: {e}")
        return None
        
    def convert_to_matter(self, usda_data: Dict) -> IngredientModel:
        """
        Converts USDA nutrient data into FIS Matter Physics.
        This is the 'Magic' translation layer.
        """
        nutrients = {n["nutrientName"]: n["value"] for n in usda_data.get("foodNutrients", [])}
        
        # 1. Physical Extraction
        water = nutrients.get("Water", 0.0)
        fat = nutrients.get("Total lipid (fat)", 0.0)
        
        # Heuristic: Water Activity based on moisture content (very rough approx)
        aw = 0.99 if water > 80 else (0.5 if water < 20 else 0.8)
        
        # 2. Flavor Extraction
        sugar = nutrients.get("Sugars, total including NLEA", 0.0)
        sodium = nutrients.get("Sodium, Na", 0.0)
        
        # Normalize (0-1) - arbitrary scale for now
        norm_sugar = min(sugar / 50.0, 1.0) # 50g sugar = max sweet
        norm_salt = min(sodium / 1000.0, 1.0) # 1000mg sodium = max salt
        norm_fat = min(fat / 100.0, 1.0)
        
        return IngredientModel(
            id=f"usda_{usda_data['fdcId']}",
            name=usda_data["description"],
            usda_id=str(usda_data["fdcId"]),
            flavor=FlavorProfile(
                sugar=norm_sugar,
                salt=norm_salt,
                lipid=norm_fat
            ),
            physical=PhysicalProperties(
                water_activity=aw,
                fat_content_percent=fat
            ),
            reaction=ReactionPotential(
                maillard_score=0.5 if norm_fat > 0.1 else 0.1 # Placeholder logic
            )
        )

if __name__ == "__main__":
    # Test
    scraper = USDAScraper()
    print("USDA Scraper initialized. Set USDA_API_KEY to function.")
