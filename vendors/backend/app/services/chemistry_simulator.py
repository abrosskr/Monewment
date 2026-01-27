import logging
import math
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class FoodChemistrySimulator:
    """
    [Food Data Factory: Phase 10 Industrial]
    Models biochemical transformations during cooking.
    Handles Frozen/Room/Hot states and 10 core reactions.
    """

    def __init__(self):
        # Activation Energies (Arrehenius-like constants, simplified for mock)
        self.kinetics = {
            "MAILLARD": {"min_temp": 140, "opt_temp": 165, "weight": 1.0},
            "CARAMELIZATION": {"min_temp": 160, "opt_temp": 180, "weight": 0.8},
            "PROTEIN_DENATURATION": {"min_temp": 50, "opt_temp": 75, "weight": 1.2},
            "GELATINIZATION": {"min_temp": 60, "opt_temp": 85, "weight": 0.7},
            "OXIDATION": {"min_temp": 20, "opt_temp": 200, "weight": -0.5}, # Negative reward for high oxidation
            "CARBONIZATION": {"min_temp": 230, "opt_temp": 300, "weight": -10.0}
        }

    def simulate_reactions(self, temp_profile: List[float], time_step: float, initial_state: str = "ROOM_TEMP") -> Dict:
        """
        Calculates the progress of 10 chemical reactions over a temperature profile.
        """
        reactions = {k: 0.0 for k in self.kinetics.keys()}
        
        # State Correction Factor
        # Frozen items require energy for phase change, slowing initial kinetics.
        kinetic_multiplier = 1.0
        if initial_state == "FROZEN":
            kinetic_multiplier = 0.3
        elif initial_state == "PREHEATED":
            kinetic_multiplier = 1.2

        for temp in temp_profile:
            # phase change logic for frozen
            if initial_state == "FROZEN" and temp > 0:
                kinetic_multiplier = min(1.0, kinetic_multiplier + 0.1)

            for rxn, params in self.kinetics.items():
                if temp >= params["min_temp"]:
                    # Arrhenius approximation (Reaction rate doubles every 10C)
                    rate = math.pow(2, (temp - params["min_temp"]) / 10) * kinetic_multiplier
                    reactions[rxn] += rate * time_step

        # Normalize and Score
        flavor_score = (reactions["MAILLARD"] * 0.6 + reactions["CARAMELIZATION"] * 0.4) / 100
        texture_score = reactions["PROTEIN_DENATURATION"] / 50
        safety_penalty = reactions["CARBONIZATION"] * 5.0
        
        return {
            "reaction_progress": reactions,
            "metrics": {
                "flavor": round(min(5.0, flavor_score), 2),
                "texture": round(min(5.0, texture_score), 2),
                "safety_risk": round(safety_penalty, 2)
            },
            "edibility": "REJECTED" if safety_penalty > 10.0 else "SAFE"
        }

    def get_industrial_recommendation(self, current_reactions: Dict, initial_state: str) -> str:
        """Heuristic-based optimization logic for RL 에이전트 가이드"""
        if initial_state == "FROZEN" and current_reactions["PROTEIN_DENATURATION"] < 0.1:
            return "LOW_HEAT_THAW_PHASE"
        if current_reactions["MAILLARD"] > 0.8:
            return "REDUCE_HEAT_TO_PREVENT_CARBONIZATION"
        return "MAINTAIN_CURRENT_GRADIENT"
