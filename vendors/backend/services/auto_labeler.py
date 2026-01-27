# app/services/auto_labeler.py
from typing import List, Dict, Any
from app.models.fis_protocol import FisFile, ChemicalVector
from app.core.taste_dna import TasteDNA

class AutoLabeler:
    """
    [The Brain Service]
    Wrapper around Core Logic (TasteDNA).
    Provides interface for other services.
    """

    @classmethod
    def classify_role(cls, name: str, mass_g: float, total_mass: float) -> str:
        """
        Delegates to Core Logic.
        """
        ratio = mass_g / total_mass if total_mass > 0 else 0
        return TasteDNA.classify_role(name, ratio)

    @classmethod
    def predict_culture(cls, ingredient_names: List[str]) -> str:
        """
        Delegates to Core Logic.
        """
        return TasteDNA.predict_culture(ingredient_names)

    @classmethod
    def predict_taste(cls, ingredients: Dict[str, float]) -> Any:
        """
        Calculates weighted sum with Fuzzy Matching for ingredient names.
        Returns a FlavorProfile object.
        """
        from app.models.matter import FlavorProfile
        total_mass = sum(ingredients.values())
        if total_mass <= 0:
            return FlavorProfile()
            
        final_v = {
            "salt": 0.0, "sugar": 0.0, "acid": 0.0, 
            "umami": 0.0, "spiciness": 0.0, "bitter": 0.0, "aroma": 0.0
        }
        
        for name, mass in ingredients.items():
            # Robust Lookup
            matched_vec = None
            name_lower = name.lower()
            
            for standard_name, vec in TasteDNA.INGREDIENT_VECTORS.items():
                if standard_name in name_lower or name_lower in standard_name:
                    matched_vec = vec
                    break
            
            if not matched_vec:
                continue

            weight = mass / total_mass
            final_v["salt"] += getattr(matched_vec, "salt", 0.0) * weight
            final_v["sugar"] += getattr(matched_vec, "sugar", 0.0) * weight
            final_v["acid"] += getattr(matched_vec, "acid", 0.0) * weight
            # Mapping glutamate -> umami
            final_v["umami"] += getattr(matched_vec, "glutamate", 0.0) * weight
            # Mapping capsaicin -> spiciness
            final_v["spiciness"] += getattr(matched_vec, "capsaicin", 0.0) * weight
            
        return FlavorProfile(**final_v)

    @classmethod
    def generate_timeline(cls, steps: List[str]) -> List[Any]:
        """
        [Action Extraction - Robust Stems]
        Translates natural language steps into robotic MachineCommands.
        """
        from app.models.machine_ir import MachineCommand, ActionType, PhysicalGoal
        timeline = []
        
        for i, step in enumerate(steps):
            action = ActionType.WAIT
            target_ing = None
            temp_c = None
            duration = None
            rpm = None
            goal = None
            
            # Simple NLP Rules using Stems
            # HEAT
            if any(k in step for k in ["볶", "튀기", "굽", "구워", "fry", "sear", "grill"]):
                action = ActionType.HEAT_SURFACE
                temp_c = 180
                goal = PhysicalGoal.MAILLARD_ONSET
            elif any(k in step for k in ["끓", "데치", "삶", "boil", "blanch"]):
                action = ActionType.HEAT_LIQUID
                temp_c = 100
                goal = PhysicalGoal.DENATURATION
            # DISPENSE
            elif any(k in step for k in ["넣", "붓", "첨가", "투하", "add", "pour"]):
                action = ActionType.DISPENSE
            # STIR
            elif any(k in step for k in ["겪", "젓", "비비", "섞", "mix", "stir"]):
                action = ActionType.STIR
                rpm = 60

            # Create Modern MachineCommand
            cmd = MachineCommand(
                step_id=i + 1,
                action=action,
                target_ingredient_id=target_ing,
                temperature_c=temp_c,
                duration_sec=duration,
                rpm=rpm,
                goal=goal
            )
            timeline.append(cmd)
            
        return timeline

    @classmethod
    def validate_identity(cls, recipe_name: str, ingredient_names: List[str]) -> Dict[str, Any]:
        """
        [Professional Identity Guard]
        Distinguishes between 'Soul' (Identity) and 'Support' (Aromatics).
        """
        found_category = None
        category_config = None
        
        for category, config in TasteDNA.CULINARY_ANCHORS.items():
            # Match if the primary name OR any alias is in the recipe name
            if category in recipe_name or any(alias.lower() in recipe_name.lower() for alias in config.get("aliases", [])):
                found_category = category
                category_config = config
                break
        
        if not category_config:
            return {"status": "UNCATEGORIZED", "score": 1.0, "message": "General dish.", "category": None}
            
        # 1. Soul Detection (Title Keyword vs Ingredient List)
        # Use the matched keyword/alias to find the 'soul' part of the title
        matched_str = next((a for a in [found_category] + config.get("aliases", []) if a.lower() in recipe_name.lower()), found_category)
        prefix = recipe_name.lower().split(matched_str.lower())[0].strip()
        
        adjectives = [
            "매콤", "맛있는", "간단", "쉬운", "황금레시피", "초간단", "대박", "인생", "극찬", 
            "비법", "최고", "정말", "진짜", "초", "쉬운", "간단한", "꿀팁", "정확한", "명품",
            "classic", "traditional", "quick", "best", "easy", "homemade", "authentic"
        ]
        clean_soul = prefix
        for adj in adjectives:
            clean_soul = clean_soul.replace(adj, "").strip()
            
        soul_found = False
        if not clean_soul: # e.g., just "Fried Rice"
            soul_found = True 
        else:
            soul_keywords = [k for k in clean_soul.split() if len(k) > 1 or k in ["밥", "죽", "국", "rice", "soup"]]
            for kw in soul_keywords:
                if any(kw.lower() in ing.lower() for ing in ingredient_names):
                    soul_found = True
                    break
        
        # 2. Structural Requirements (Necessary for the technique)
        # Check both Korean and English anchors
        struct_matched = [s for s in config["structure"] if any(s.lower() in ing.lower() for ing in ingredient_names)]
        
        # 3. Aromatic Audit (Purely Optional / Support)
        aroma_found = [a for a in config["optional_aromatics"] if any(a.lower() in ing.lower() for ing in ingredient_names)]
        
        # Final Determination
        if not soul_found and clean_soul:
            status = "DUBIOUS"
            message = f"Identity Mismatch: '{clean_soul}' promised in title, but not found in ingredients."
            score = 0.2
        elif not struct_matched:
            status = "IMCOMPLETE"
            message = f"Lacks structural base for {found_category} (e.g., Oil/Seasoning)."
            score = 0.5
        else:
            status = "AUTHENTIC"
            message = f"Authentic {found_category} identity confirmed."
            if aroma_found:
                message += f" (Enhanced with aromatics: {', '.join(aroma_found)})"
            score = 1.0
            
        return {
            "status": status,
            "score": score,
            "message": message,
            "category": found_category,
            "soul_ingredient": clean_soul,
            "aromatics": aroma_found
        }

    @classmethod
    def suggest_improvements(cls, category: str, ingredient_names: List[str]) -> List[str]:
        """
        [Culinary Guide]
        Suggests global techniques to enhance traditional dishes.
        """
        suggestions = []
        if category == "볶음밥":
            suggestions.append("Searing Strategy: Sear the meat at 220°C before adding rice for Maillard reaction.")
            if "참기름" in str(ingredient_names):
                suggestions.append("Finishing Oil: Add sesame oil only at the final stage to preserve aroma from heat degradation.")
        elif category == "찌개":
            suggestions.append("Umami Layering: Start with a 'Dashi' or kelp base for deeper glutamate profile.")
        
        return suggestions
