# app/services/normalizer_service.py
import re
from typing import Dict, List, Any
from app.models.fis_protocol import FisFile, MachineCommand, ActionType
from app.core.fis_physics import FisPhysics
from app.core.logging import logger

class RecipeNormalizer:
    """
    [The Translator Service]
    Converts extracted natural language components into formal FIS physics commands.
    """

    def analyze_context(self, action_verb: str, ingredients: List[str]) -> Dict[str, Any]:
        """
        Determines target temperature and physics phenomena based on context.
        """
        phy_result = FisPhysics.get_target_temp(action_verb, ingredients)
        return {
            "target_temp": phy_result["surface_temp"],
            "physics_goal": phy_result["phenomenon"],
            "reaction_intensity": phy_result.get("reaction_intensity", 0.0),
            "core_temp_estimate": phy_result.get("core_temp_estimate", 25.0),
            "overcook_risk": phy_result.get("overcook_risk", 0.0)
        }

    def calculate_seasoning(self, total_mass_g: float, target_type: str) -> float:
        """
        Calculates required seasoning mass based on isotonic targets.
        """
        ratio = 0.0
        if target_type == "SALT_PINCH":
            ratio = 0.001
        elif target_type == "FULL_SEASONING":
             ratio = FisPhysics.TARGET_RATIOS["SALINITY"]
             
        return FisPhysics.calculate_seasoning_mass(total_mass_g, ratio)

    def convert_to_fis_command(self, original_step: str, seq: int, context_ingredients: List[str] = []) -> MachineCommand:
        """
        Final Step: Text -> FIS Command Object (Physics Compliant)
        """
        lower_text = original_step.lower()
        logger.debug(f"Normalizing step {seq}: {original_step[:30]}...")
        
        # 1. Action Inferencing
        action = ActionType.NOTIFY
        target = "Human"
        params = {"msg": original_step}

        if any(v in lower_text for v in ["fry", "boil", "sear", "stew", "simmer"]):
            action = ActionType.HEAT
            target = "Induction_Main"
            
            # 2. Physics-based Temp Calculation
            phy_context = self.analyze_context(lower_text, context_ingredients)
            target_temp = phy_context["target_temp"]
            
            # 3. Thermal Dynamics: Dynamic Duration
            total_mass = 0
            weighted_specific_heat = 0
            
            if not context_ingredients:
                total_mass = 500
                avg_sh = 3.5 # Water-like
            else:
                for ing in context_ingredients:
                    props = FisPhysics.get_physics_properties(ing)
                    total_mass += 250 # Assume 250g per detected ingredient for now
                    weighted_specific_heat += props.get("specific_heat", 2.0)
                avg_sh = weighted_specific_heat / len(context_ingredients)
            
            current_temp = 20.0 # Ambient
            duration = FisPhysics.calculate_cooking_duration(
                mass_g=total_mass,
                specific_heat=avg_sh,
                delta_temp=target_temp - current_temp
            )
                
            params = {
                "temp": target_temp,
                "physics_goal": phy_context["physics_goal"],
                "duration": duration,
                "reaction_intensity": phy_context["reaction_intensity"],
                "core_temp_predicted": phy_context["core_temp_estimate"],
                "overcook_risk": phy_context["overcook_risk"]
            }

        return MachineCommand(
            id=f"CMD_{seq:03d}",
            sequence_no=seq,
            action=action,
            target=target,
            params=params
        )
