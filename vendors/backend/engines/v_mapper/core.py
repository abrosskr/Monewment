from typing import Dict, List, Any
from pydantic import BaseModel
from app.core.fis_physics import PhysicsReactor

class FidelityReport(BaseModel):
    taste_fidelity: float      # 0.0 to 1.0 (99% = 0.99)
    maillard_match: float
    moisture_match: float
    aroma_match: float
    bottleneck_reason: str

class VMapperEngine:
    """
    [V-Mapper]
    Cross-Hardware Flavor Mapping Engine.
    Compares 'Gold Standard' (Chef/Pro) physics with 'Home Target' physics.
    Calculates the 'Taste Fidelity' and identifies gaps.
    """

    @classmethod
    def compare_states(cls, baseline: PhysicsReactor, target: PhysicsReactor) -> FidelityReport:
        """
        Calculates similarity between two physics states.
        Focuses on Integrated Reaction Progress and Moisture levels.
        """
        # 1. Maillard Match (Logarithmic similarity)
        m_base = baseline.reaction_progress.get("MAILLARD", 0)
        m_target = target.reaction_progress.get("MAILLARD", 0)
        maillard_sim = 1.0 - abs(m_base - m_target) / max(m_base, 1e-6) if m_base > 0 else 1.0
        
        # 2. Moisture Match
        w_base = baseline.ingredients.get("water", 0) / max(baseline.total_mass_g, 1e-6)
        w_target = target.ingredients.get("water", 0) / max(target.total_mass_g, 1e-6)
        moisture_sim = 1.0 - abs(w_base - w_target) / max(w_base, 1e-6) if w_base > 0 else 1.0
        
        # 3. Overall Fidelity (Weighted)
        fidelity = (maillard_sim * 0.6) + (moisture_sim * 0.4)
        
        reason = "OK"
        if maillard_sim < 0.8: reason = "Thermal intensity insufficient for Maillard"
        elif moisture_sim < 0.8: reason = "Excessive moisture loss in home environment"

        return FidelityReport(
            taste_fidelity=max(0, round(fidelity, 3)),
            maillard_match=round(maillard_sim, 3),
            moisture_match=round(moisture_sim, 3),
            aroma_match=1.0, # Placeholder
            bottleneck_reason=reason
        )
