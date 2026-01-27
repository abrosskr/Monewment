import math
from typing import Dict, Any, Optional
from pydantic import BaseModel

class DiffusionContext(BaseModel):
    diffusivity: float = 0.14e-6 # Thermal diffusivity (m^2/s)
    characteristic_length: float = 0.02 # Meters (e.g. radius of object)
    biot_number: float = 5.0 # Ratio of internal to surface heat resistance

class VDiffusivityEngine:
    """
    [V-Diffusivity: Material-Aware Heat Transfer]
    Calculates Thermal Diffusivity (alpha) based on ingredient composition:
    alpha = k / (rho * cp)
    Where k (Thermal Conductivity) is derived from Water/Fat/Protein ratios.
    """

    @classmethod
    def calculate_material_alpha(cls, water_ratio: float, fat_ratio: float, density: float = 1000.0, cp: float = 3500.0) -> float:
        """
        Estimated Thermal Conductivity (k) using Choi-Okos model components:
        k_water ~ 0.6, k_fat ~ 0.15, k_protein ~ 0.2
        """
        k_eff = (0.6 * water_ratio) + (0.15 * fat_ratio) + (0.2 * (1.0 - water_ratio - fat_ratio))
        alpha = k_eff / (density * cp)
        return max(alpha, 1e-8) # m^2/s

    @classmethod
    def get_context(cls, thickness_mm: float, water_ratio: float, fat_ratio: float) -> DiffusionContext:
        """Creates a context based on actual geometry and composition."""
        alpha = cls.calculate_material_alpha(water_ratio, fat_ratio)
        L = (thickness_mm / 1000.0) / 2.0 # Half-thickness for heat penetration from both sides
        return DiffusionContext(
            diffusivity=alpha,
            characteristic_length=max(L, 0.001), # Min 1mm
            biot_number=5.0
        )

    @classmethod
    def calculate_fourier_number(cls, duration: float, context: DiffusionContext) -> float:
        """Fo = alpha * t / L^2"""
        return (context.diffusivity * duration) / (context.characteristic_length**2)

    @classmethod
    def estimate_core_temperature(cls, 
                                  surface_temp: float, 
                                  initial_temp: float, 
                                  duration: float, 
                                  context: DiffusionContext) -> Dict[str, float]:
        """
        Uses simplified lumped-capacitance / Fourier analysis to find core temp.
        Theta = (T_core - T_inf) / (T_ini - T_inf) = exp(-Bi * Fo)
        """
        fo = cls.calculate_fourier_number(duration, context)
        theta = math.exp(-context.biot_number * fo)
        
        core_temp = surface_temp - (surface_temp - initial_temp) * theta
        
        return {
            "core_temp": round(core_temp, 2),
            "heat_lag_factor": round(theta, 4),
            "fourier_number": round(fo, 4)
        }

    @classmethod
    def predict_overcook_risk(cls, core_temp: float, target_temp: float, duration: float) -> float:
        """Integral of temperature exceeded over time (Hazard-Time Index)."""
        temp_delta = max(0, core_temp - target_temp)
        return round(temp_delta * (duration / 60.0), 3)
