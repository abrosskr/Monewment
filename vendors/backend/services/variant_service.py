from typing import Dict, Any, List

class VariantService:
    """
    [The Persona Service]
    Resolves the "Dongpo Pork Dilemma".
    Selects the right variant based on Authenticity (Auth) vs Convenience (Conv).
    """

    @classmethod
    def select_variant(cls, recipe_base_name: str, user_profile: Dict[str, Any]) -> str:
        """
        Returns the specific variant name.
        """
        auth_level = user_profile.get("authenticity_preference", "LOW").upper() # HIGH/LOW
        conv_level = user_profile.get("convenience_preference", "HIGH").upper() # HIGH/LOW
        
        # Mock Database of Variants
        # In production, this allows querying `SELECT * FROM recipes WHERE variant_tags IN (...)`
        
        if "dongpo" in recipe_base_name.lower() or "pork belly" in recipe_base_name.lower():
            if auth_level == "HIGH" and conv_level == "LOW":
                return "Hangzhou Authentic Dongpo Pork (3hr Slow Cook)"
            elif auth_level == "LOW" and conv_level == "HIGH":
                return "K-Style Quick Dongpo Pork (Pressure Cooker)"
            elif auth_level == "LOW" and conv_level == "LOW":
                return "Korean Fusion Dongpo Pork (Plum Extract)"
            else:
                 return "Standard Dongpo Pork"
                 
        return recipe_base_name # No variant found
