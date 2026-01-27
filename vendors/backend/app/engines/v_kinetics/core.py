import math
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class ReactionModel(BaseModel):
    name: str
    A: float  # Pre-exponential factor
    Ea: float # Activation Energy (J/mol)
    Cf: float # Calibration factor

class KineticsState(BaseModel):
    progress: Dict[str, float] = {} # Name: progress (0-10 scale)

class VKineticsEngine:
    """
    [V-Kinetics] 
    Industry-agnostic Arrhenius Reaction Engine.
    Used for Maillard, Caramelization, or Industrial Chemical Synthesis.
    """
    R = 8.314 # Gas Constant

    @classmethod
    def calculate_rate_constant(cls, temp_c: float, model: ReactionModel) -> float:
        """Calculates k using Arrhenius equation: k = A * exp(-Ea / RT)"""
        temp_k = temp_c + 273.15
        try:
            return model.A * math.exp(-model.Ea / (cls.R * temp_k))
        except (OverflowError, ZeroDivisionError):
            return 0.0

    @classmethod
    def calculate_moisture_correction(cls, water_mass_ratio: float) -> float:
        """
        [The Moisture-Maillard Paradox Solver]
        Maillard reaction peaks at aw (water activity) of 0.6-0.7.
        Too much water -> dilution, Too little water -> lack of mobility.
        Using a Gaussian bell-curve approximation around peak 0.65.
        """
        peak_aw = 0.65
        sigma = 0.25 # Spread of the curve
        return math.exp(-((water_mass_ratio - peak_aw)**2) / (2 * sigma**2))

    @classmethod
    def step_progress(cls, 
                      current_progress: float, 
                      temp_c: float, 
                      dt: float, 
                      model: ReactionModel,
                      water_mass_ratio: float = 0.7) -> float:
        """Evolves reaction progress over dt seconds with moisture correction."""
        k = cls.calculate_rate_constant(temp_c, model)
        moisture_factor = cls.calculate_moisture_correction(water_mass_ratio)
        delta = k * dt * model.Cf * moisture_factor
        return min(10.0, current_progress + delta)
