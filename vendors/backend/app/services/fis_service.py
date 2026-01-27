import numpy as np
from scipy.optimize import lsq_linear
from app.core.logging import logger
from sqlalchemy.orm import Session
from app.services.chemical_service import ChemicalService

class FisService:
    """
    [Flavor Inkjet System - DB Connected]
    Calculates the optimal mix of 'Ink Elements' to recreate a target flavor vector.
    Uses ChemicalService (DB-backed) to get ink vectors.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.chem_service = ChemicalService(db)

    def optimize_recipe(self, target_vector: list):
        """
        Input: [Salt, Sweet, Umami, Spicy, Sour] (5D Vector)
        Output: Dictionary of Pump Instructions (ml)
        """
        if len(target_vector) != 5:
            raise ValueError("Target vector must be 5-dimensional [Salt, Sweet, Umami, Spicy, Sour]")
            
        target = np.array(target_vector)
        logger.info(f"🧪 [FIS] Optimizing for target: {target_vector}")
        
        # 1. Fetch Inks from DB via ChemicalService
        inks = self.chem_service.get_available_inks()
        
        # 2. Build INK MATRIX dynamically
        # We need to map Chemical Composition -> standard 5D Flavor Vector
        # This mapping is heuristic relative to human perception thresholds.
        # For MVP, we define a mapping from Compound -> Flavor Index
        # Salt=0, Sweet=1, Umami=2, Spicy=3, Sour=4
        compound_map = {
            "NaCl": 0, "Sucrose": 1, "Glutamate": 2, 
            "Capsaicin": 3, "Acetic_Acid": 4
        }
        
        ink_vectors = []
        ink_names = []
        
        for ink in inks:
            # Parse composition
            compounds = ink.chemical_json or {}
            if isinstance(compounds, str):
                import json
                try: compounds = json.loads(compounds)
                except: compounds = {}

            # Convert compounds to 5D vector
            vec = np.zeros(5)
            for comp, ratio in compounds.items():
                idx = compound_map.get(comp)
                if idx is not None:
                    # Scaling Factor: Chemical Amount -> Perceived Intensity
                    # e.g., Capsaicin is way more potent than Sugar. 
                    # For this prototype, we use arbitrary multipliers to match legacy hardcoded values.
                    multiplier = 10.0 
                    if comp == "Capsaicin": multiplier = 5000.0
                    elif comp == "Sucrose": multiplier = 13.0
                    elif comp == "NaCl": multiplier = 20.0
                    elif comp == "Glutamate": multiplier = 100.0
                    elif comp == "Acetic_Acid": multiplier = 30.0
                    
                    vec[idx] += (ratio * multiplier)
            
            ink_vectors.append(vec)
            ink_names.append(ink.product_name)
            
        if not ink_vectors:
             return {"error": "No Inks loaded from DB"}
             
        matrix = np.array(ink_vectors).T # Transpose for linear algebra
        
        # 3. Solver
        res = lsq_linear(matrix, target, bounds=(0, np.inf))
        
        if not res.success:
            logger.error(f"❌ [FIS] Optimization failed: {res.message}")
            return {"status": "failed", "error": "Optimization failed"}
            
        # Format Result
        recipe = {}
        for name, amount in zip(ink_names, res.x):
            if amount > 0.05: # Filter negligible amounts
                recipe[name] = round(float(amount), 2)
                
        # Calculate Simulated Result
        simulated = matrix @ res.x
        error = np.linalg.norm(target - simulated)
        
        logger.info(f"✅ [FIS] Recipe found with error rate: {error:.4f}")
        
        return {
            "status": "success",
            "recipe": recipe,
            "simulated_taste": simulated.tolist(),
            "error_rate": float(error)
        }
