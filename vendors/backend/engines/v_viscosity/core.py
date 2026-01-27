import math
from typing import Dict, List, Any
from pydantic import BaseModel

class FluidProperties(BaseModel):
    viscosity_cp: float
    ph: float
    weight_fraction: float = 1.0

class VViscosityEngine:
    """
    [V-Viscosity]
    Manages non-linear fluid property changes.
    Supports Non-Newtonian (Power-law) fluid behavior.
    """

    @classmethod
    def calculate_concentration_factor(cls, initial_mass: float, final_mass: float) -> float:
        return initial_mass / max(final_mass, 1e-6)

    @classmethod
    def blend_and_concentrate(cls, 
                               fluids: List[FluidProperties], 
                               concentration_factor: float,
                               shear_rate: float = 1.0) -> Dict[str, float]:
        """
        [Non-Newtonian Orchestration]
        Calculates apparent viscosity based on concentration and shear rate.
        mu_eff = K * (shear_rate)^(n-1) * (conc_factor)^p
        """
        total_h_conc = 0.0
        total_ln_visc = 0.0
        # Flow behavior index (n < 1: Shear-thinning, n = 1: Newtonian)
        n = 0.65 
        
        for fluid in fluids:
            # pH to H+ concentration (with concentration factor)
            h_conc = (10 ** (-fluid.ph)) * concentration_factor
            total_h_conc += h_conc * fluid.weight_fraction
            
            # Non-Newtonian Effect (Shear-thinning)
            # Consistency index K increases with concentration
            k_eff = fluid.viscosity_cp * (concentration_factor ** 2.0)
            apparent_visc = k_eff * (max(shear_rate, 0.1) ** (n - 1))
            
            total_ln_visc += math.log(max(apparent_visc, 1e-6)) * fluid.weight_fraction
            
        final_ph = -math.log10(max(total_h_conc, 1e-14))
        final_visc = math.exp(total_ln_visc)
        
        return {
            "ph": round(final_ph, 2),
            "viscosity_cp": round(final_visc, 2),
            "thickness_relative": round(concentration_factor, 3)
        }
