import math
from typing import Dict, Any, List
from pydantic import BaseModel

class SurfaceState(BaseModel):
    coating_integrity: float = 1.0     # 0.0 (Destroyed) to 1.0 (Factory New)
    oil_film_density: float = 1.0      # 0.0 (Dry/Sticking) to 1.0 (Perfectly Seasoned)
    carbon_build_up: float = 0.0       # Accumulated burnt residue
    adhesion_risk: float = 0.0         # Current likelihood of food sticking

class SurfaceObservation(BaseModel):
    pan_temp: float
    food_surface_temp: float          # Inferred or measured
    heat_flux: float                   # Watts/m^2

class VSurfaceEngine:
    """
    [V-Surface]
    Tribological & Surface Condition Engine.
    Detects coating degradation and oil film (seasoning) status.
    Fixes the 'ideal surface' fallacy in physical simulations.
    """

    @classmethod
    def analyze_adhesion_risk(cls, state: SurfaceState, temp_c: float) -> float:
        """
        Calculates sticking probability based on Lecithin breakdown and Surface energy.
        Sticking probability increases exponentially as oil film depletes or coating fails.
        """
        # Bonding threshold for many proteins is ~140C
        bonding_factor = max(0, (temp_c - 140) / 100.0)
        
        # Risk = (1 - Quality) * Bonding_Potential * (1 - Oil_Film)
        risk = (1.1 - state.coating_integrity) * bonding_factor * (1.1 - state.oil_film_density)
        return min(1.0, risk)

    @classmethod
    def infer_surface_health(cls, obs: SurfaceObservation) -> Dict[str, float]:
        """
        [Thermal Resistance Analysis]
        Infers surface state by the temp delta between Pan and Food.
        R_contact = (T_pan - T_food) / Heat_Flux
        If R_contact is too high -> Sticking/Insulation layer (Carbonization).
        If R_contact is too low -> Metal-to-Metal (Coating gone).
        """
        if obs.heat_flux <= 0: return {"resistance": 0, "health_impact": 0}
        
        r_contact = (obs.pan_temp - obs.food_surface_temp) / obs.heat_flux
        
        # Heuristic: Normal R_contact for oiled pan is ~0.005-0.015 K*m^2/W
        health_impact = 0.0
        if r_contact > 0.05: # Too much resistance -> Burning/Sticking carbon layer
             health_impact = -0.1
        elif r_contact < 0.001: # Too little -> No non-stick buffer
             health_impact = -0.05
             
        return {"r_contact": r_contact, "health_impact": health_impact}

    @classmethod
    def apply_aging_effect(cls, state: SurfaceState, temp_c: float, dt: float) -> SurfaceState:
        """
        Simulates the degradation of coating or oil film over time at high heat.
        Oil film burns off above 230C (Smoke point).
        """
        if temp_c > 230.0:
            burn_rate = 0.001 * (temp_c / 230.0) # Burn 0.1% per second at smoke point
            state.oil_film_density = max(0.0, state.oil_film_density - (burn_rate * dt))
            
        if temp_c > 350.0: # PTFE (Teflon) breakdown threshold
            state.coating_integrity = max(0.0, state.coating_integrity - (0.005 * dt))
            
        return state
