from typing import List, Dict, Optional
import os
import json
import datetime
from app.models.matter import IngredientModel, FlavorProfile, PhysicalProperties, ReactionPotential, TrustTier, SourceMetadata
from app.scrapers.usda_connector import USDAScraper

class MatterETL:
    """
    [Phase 6: The Clean Factory]
    Ingests raw data but strictly separates sources.
    NO Flavor Forgery allowed.
    """
    
    def __init__(self):
        self.usda = USDAScraper()
        
    def transform_usda_item(self, usda_data: Dict) -> IngredientModel:
        """
        Transforms USDA data into IngredientModel.
        CRITICAL: Only populates Physical Properties. Leaves Flavor blank (or explicit Unknown).
        """
        nutrients = {n["nutrientName"]: n["value"] for n in usda_data.get("foodNutrients", [])}
        
        # 1. Physical Props (Trust: B - Text Explicit from USDA)
        water = nutrients.get("Water", 0.0)
        fat = nutrients.get("Total lipid (fat)", 0.0)
        
        # Heuristic for Water Activity (Tier D - Heuristic, but better than nothing)
        # Real logic would need more complex formulas
        aw = 0.99 if water > 80 else (0.5 if water < 20 else 0.8)
        
        physical = PhysicalProperties(
            water_activity=aw,
            fat_content_percent=fat,
            state="Solid" if water < 80 else "Liquid" # Simple heuristic
        )
        
        # 2. Flavor Profile (Trust: U - Unknown)
        # WE DO NOT INFER FLAVOR FROM CALORIES. 
        # This prevents "Scientific Forgery".
        flavor = FlavorProfile(
            # Explicitly empty. 
            # In a real ETL, we would join with FlavorDB here.
        )
        
        # 3. Construct Model
        model = IngredientModel(
            id=f"usda_{usda_data['fdcId']}",
            name=usda_data["description"],
            usda_id=str(usda_data["fdcId"]),
            flavor=flavor,
            physical=physical,
            reaction=ReactionPotential(), # Empty for now
            trust_tier=TrustTier.B # Base data is good
        )
        
        # 4. Set Metadata
        model.set_trust(TrustTier.B, "USDA_FoodData_Central", 0.95)
        
        # Mark Flavor as Unknown to safeguard Edibility Engine
        # (This logic would be expanded in production)
        
        return model

    def run_batch(self, query: str, limit: int = 5, mock_data: Optional[Dict] = None) -> List[IngredientModel]:
        """
        Batch ingestion simulation.
        """
        results = []
        
        if mock_data:
            print(f"ETL: [MOCK MODE] Processing '{query}'...")
            raw_item = mock_data
        else:
            print(f"ETL: Searching USDA for '{query}'...")
            raw_item = self.usda.search_food(query)
            
        if raw_item:
            model = self.transform_usda_item(raw_item)
            results.append(model)
            print(f"ETL: Ingested '{model.name}' [Tier: {model.trust_tier.value}]")
            print(f"     -> Physics Detected: Water={model.physical.water_activity}, Fat={model.physical.fat_content_percent}")
            print(f"     -> Flavor Status: {model.flavor.dict()}") # Should be mostly 0/Empty
        else:
            print("ETL: No data found.")
            
        return results

if __name__ == "__main__":
    # Test Run
    etl = MatterETL()
    etl.run_batch("Cheddar Cheese")
