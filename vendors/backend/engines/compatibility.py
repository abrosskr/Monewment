from typing import List, Dict, Optional
from pydantic import BaseModel
from app.models.matter import IngredientModel

class EdibilityIssue(BaseModel):
    severity: str # "CRITICAL" | "WARNING"
    rule_id: str
    message: str

class CompatibilityEngine:
    """
    [The Firewall]
    Validates recipe stability based on Food Physics rules.
    Prevents 'Gross' combinations.
    """
    
    @staticmethod
    def check_stability(ingredients: List[IngredientModel]) -> List[EdibilityIssue]:
        issues = []
        
        # 1. Acid-Dairy Curdling Rule (Contextual)
        # If Acidic ingredient + Dairy ingredient -> Check for Stabilizers
        dairy = [i for i in ingredients if "milk" in i.name.lower() or "cream" in i.name.lower() or "cheese" in i.name.lower()]
        acids = [i for i in ingredients if i.flavor.acid > 0.6]
        
        if dairy and acids:
            # Context Check: Is it stabilized?
            # Stabilizers: High Fat (>30%), Starch (Flour/Potato), or Emulsifiers
            is_stabilized = False
            stabilizer_source = None
            
            # Check Fat in Dairy itself (Heavy Cream is stable)
            for d in dairy:
                if d.physical.fat_content_percent > 30.0:
                    is_stabilized = True
                    stabilizer_source = f"High Fat Dairy ({d.name})"
            
            # Check external stabilizers (Starch, Fat)
            for i in ingredients:
                if "starch" in i.name.lower() or "flour" in i.name.lower() or "potato" in i.name.lower():
                    is_stabilized = True
                    stabilizer_source = f"Starch ({i.name})"
            
            if is_stabilized:
                 issues.append(EdibilityIssue(
                    severity="INFO", # Downgraded from WARNING
                    rule_id="CHEM_CURDLE_STABILIZED",
                    message=f"Acid({acids[0].name}) + Dairy({dairy[0].name}) detected but stabilized by {stabilizer_source}. Safe to cook."
                ))
            else:
                issues.append(EdibilityIssue(
                    severity="WARNING",
                    rule_id="CHEM_CURDLE_RISK",
                    message=f"Risk of curdling: High acid source '{acids[0].name}' mixed with unstabilized Dairy '{dairy[0].name}'."
                ))
            
        # 2. Texture Feasibility (Moisture Check)
        # If total water activity is too low for a 'Stew'
        total_mass = 100 # Dummy mass
        # Real logic would calculate weighted average of water content
        
        return issues

    @classmethod
    def validate_recipe(cls, recipe_name: str, ingredient_models: List[IngredientModel]):
        result = {
            "recipe": recipe_name,
            "compatible": True,
            "issues": []
        }
        
        issues = cls.check_stability(ingredient_models)
        if issues:
            result["issues"] = [i.dict() for i in issues]
            if any(i.severity == "CRITICAL" for i in issues):
                result["compatible"] = False
                
        return result
