import math
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class PulseReading(BaseModel):
    temp: float
    time: float
    power: float

class HardwareProfile(BaseModel):
    inferred_thermal_mass: float  # m * Cp
    heat_loss_estimated: float
    confidence: float

class VProfilerEngine:
    """
    [V-Profiler]
    Hardware Inference Engine.
    Identifies vessel properties through 'Thermal Pulse' analysis.
    Eliminates the need for manual hardware data entry.
    """

    @classmethod
    def infer_vessel_properties(cls, readings: List[PulseReading]) -> HardwareProfile:
        """
        Analyzes a heating pulse to derive thermal mass (mc_p).
        Q = mc_p * dT  =>  mc_p = (Power * Efficiency * dt) / dT
        """
        if len(readings) < 2:
            return HardwareProfile(inferred_thermal_mass=0, heat_loss_estimated=0, confidence=0)

        dt = readings[-1].time - readings[0].time
        dT = readings[-1].temp - readings[0].temp
        avg_power = sum(r.power for r in readings) / len(readings)
        
        # Approximate efficiency (standard 85%)
        net_energy_in = avg_power * 0.85 * dt
        
        if dT <= 0: return HardwareProfile(inferred_thermal_mass=1000, heat_loss_estimated=5, confidence=0.1)
        
        thermal_mass = net_energy_in / dT
        
        return HardwareProfile(
            inferred_thermal_mass=round(thermal_mass, 2),
            heat_loss_estimated=12.0, # Default until cooling pulse analysis
            confidence=0.85 if dt > 10 else 0.5
        )
