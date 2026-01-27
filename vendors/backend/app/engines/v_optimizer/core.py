from typing import Dict, Any, List
from pydantic import BaseModel

class OptimizationGoal(BaseModel):
    target_finish_time_s: float
    urgency_level: str = "NORMAL" # NORMAL, PEAK, CRITICAL (Turbo)

class OptimizedInstruction(BaseModel):
    recommended_power_watts: float
    estimated_quality_loss: float # Due to rapid heating (thermal lag)
    risk_headroom: float

class VOptimizerEngine:
    """
    [V-Optimizer]
    Response Strategy Engine for "Peak Orders".
    Scales power and sequence based on urgency while balancing TSR and Quality.
    """

    @classmethod
    def calculate_turbo_trajectory(cls, 
                                   current_temp: float, 
                                   target_temp: float, 
                                   thermal_mass: float,
                                   goal: OptimizationGoal) -> OptimizedInstruction:
        """
        Calculates the power required to reach target_temp by target_finish_time.
        P = (mc_p * dT) / t_remaining
        """
        dT = target_temp - current_temp
        if dT <= 0: return OptimizedInstruction(recommended_power_watts=0, estimated_quality_loss=0, risk_headroom=1.0)

        required_power = (thermal_mass * dT) / max(goal.target_finish_time_s, 1.0)
        
        # Max hardware limit (e.g. 3000W)
        capped_power = min(required_power, 3000.0)
        
        # Penalty for speed: High power increases the core/surface temp gap (Thermal Lag)
        quality_loss = (capped_power / 1000.0) * 0.1 # Heuristic
        
        return OptimizedInstruction(
            recommended_power_watts=round(capped_power, 0),
            estimated_quality_loss=round(quality_loss, 3),
            risk_headroom=max(0, (3000 - capped_power) / 3000)
        )

    @classmethod
    def adapt_recipe(cls, 
                     pro_baseline: Dict[str, Any], 
                     home_hardware_eff: float) -> Dict[str, Any]:
        """
        [The Recipe Translator]
        Converts a pro-level recipe (e.g. 3000W Gas) to a home-level equivalent.
        If fidelity is low, it suggests 'Method Modification' (e.g. Pre-heating, Duration ext).
        """
        pro_energy = pro_baseline["power"] * pro_baseline["duration"] * 0.8 # Pro Assume 80%
        
        # How much time we need at home (with lower efficiency) to match total energy
        home_duration = pro_energy / (1500 * home_hardware_eff)
        
        fidelity_loss = 0.0
        recommendations = []
        preheat_temp = 23.0
        modified_ingredients = {}

        if home_hardware_eff < 0.5: # Gas or weak induction
            fidelity_loss = 0.01 
            preheat_temp = 220.0 
            recommendations.append("Execute 'Staged Hydration': Add liquid in 3 increments (30%, 30%, 40%)")
            recommendations.append("Pre-heat vessel to 220C")
            home_duration = pro_baseline["duration"] * 1.8 # Allow more time for staged reduction
            modified_ingredients = {"water_staged": True, "reduction_ratio": 0.8}
        else:
            recommendations.append("Standard home induction is sufficient")

        return {
            "adapted_duration": round(home_duration, 1),
            "preheat_temp": preheat_temp,
            "modified_ingredients": modified_ingredients,
            "predicted_fidelity": round(1.0 - fidelity_loss, 2),
            "recommendations": recommendations
        }
