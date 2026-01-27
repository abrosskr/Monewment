# app/services/chemical_service.py
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.engines.product_standard.models import ProductMaster
from app.engines.product_standard.interface import ProductStandardInterface

class ChemicalService:
    """
    [FOT Engine Phase 2 - DB Connected]
    Manages Inks and converts 'Target Chemical Vectors' into 'Ink Pump Instructions'
    by querying the ProductStandard DB.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.product_api = ProductStandardInterface(db)
        
    def get_available_inks(self) -> List[ProductMaster]:
        """
        Fetches all active Inks from the Master DB.
        """
        return self.db.query(ProductMaster).filter(
            ProductMaster.is_ink == True
        ).all()

    def convert_to_chemicals(self, ingredients: Dict[str, float]) -> Dict[str, float]:
        """
        Input: {"Soy Sauce": 10.0 (g), "Sugar": 5.0 (g)}
        Output: {"NaCl": 1.5, "Sucrose": 5.0, ...}
        
        Uses ProductMaster 'chemical_json' as Single Source of Truth.
        """
        total_chemicals = {}
        
        for name, weight in ingredients.items():
            # 1. Find Product (Fuzzy Match for now, or use mapped GTIN if available)
            # In a real system, 'ingredients' keys should be GTINs or mapped names.
            # Here we try to search by name.
            products = self.product_api.search_by_name(name)
            
            if not products:
                print(f"⚠️ Warning: Unknown ingredient '{name}'. Treating as inert.")
                continue
                
            # Use the first match (Best match)
            product = products[0] 
            
            if not product.chemical_json:
                 print(f"⚠️ Warning: Product '{product.product_name}' has no chemical profile.")
                 continue
                 
            # 2. Accumulate
            # chemical_json structure: {"NaCl": 0.15, "Water": 0.8} (Ratio per 1 unit)
            # Ensure proper JSON parsing
            compounds = product.chemical_json
            if isinstance(compounds, str):
                import json
                try: compounds = json.loads(compounds)
                except: compounds = {}
            
            for comp, ratio in compounds.items():
                amount = weight * ratio
                total_chemicals[comp] = total_chemicals.get(comp, 0.0) + amount
                
        return total_chemicals

    def calculate_ink_usage(self, chemical_vector: Dict[str, float]) -> Dict[str, float]:
        """
        Input: {"NaCl": 1.5, "Sucrose": 5.0} (Target Mass)
        Output: {"FIS-INK-005": 6.0 (mL), ...}
        
        Dynamic Solver using available Inks from DB.
        """
        available_inks = self.get_available_inks()
        recipe = {} # {Brand/Name: Volume}
        remaining_target = chemical_vector.copy()
        
        # Helper: Find best ink for a specific chemical
        def find_ink_for_chemical(chem_name):
            best_ink = None
            max_concentration = 0.0
            for ink in available_inks:
                # Parse JSON
                compounds = ink.chemical_json or {}
                if isinstance(compounds, str):
                    import json
                    try: compounds = json.loads(compounds)
                    except: compounds = {}
                
                conc = compounds.get(chem_name, 0.0)
                if conc > max_concentration:
                    max_concentration = conc
                    best_ink = ink
            return best_ink, max_concentration

        # Strategy: Greedy Allocation
        # Iterate through target chemicals
        for chem, target_mass in remaining_target.items():
            if target_mass <= 0: continue
            
            ink, concentration = find_ink_for_chemical(chem)
            
            if ink and concentration > 0:
                required_vol = target_mass / concentration
                
                # Add to recipe (Using Product Name for readability, or GTIN)
                key = ink.product_name # "05_Salt_Brine"
                recipe[key] = recipe.get(key, 0.0) + required_vol
                
                # Deduct from target (Simplified: assuming ink is pure source for this greedy step)
                # In strict logic, we should subtract ALL side-effects of this ink from remaining_target.
                # Implementing Side-Effect Subtraction:
                compounds = ink.chemical_json or {}
                if isinstance(compounds, str):
                    import json
                    try: compounds = json.loads(compounds)
                    except: compounds = {}
                    
                for c, rat in compounds.items():
                    if c in remaining_target:
                        remaining_target[c] -= (required_vol * rat)

        return {k: round(v, 2) for k, v in recipe.items() if v > 0.05}
