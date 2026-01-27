import math
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class SafetyContext(BaseModel):
    """
    [VANDORS TSR - Agnostic Safety Context]
    Can be used for Cooking, Data Centers, or Industrial Reactors.
    """
    hazard_activation_energy: float = 75000  # J/mol (Ea)
    critical_threshold_temp: float = 230.0   # °C
    warning_buffer_seconds: float = 60.0
    critical_buffer_seconds: float = 30.0
    max_degradation_allowed: float = 1.0     # Normalized 0 to 1

class TSRState(BaseModel):
    """Current state of the thermal safety monitoring."""
    cumulative_risk: float = 0.0
    degradation_index: float = 0.0
    peak_slope: float = 0.0
    risk_level: str = "SAFE"
    safe_time_remaining: float = 999.0
    last_temp: Optional[float] = None

class VTsrCore:
    """
    V-TSR (Thermal Stability & Risk) Core Engine.
    High-precision thermal hazard tracking and runaway prediction.
    """
    
    @staticmethod
    def calculate_hazard(temp_c: float, context: SafetyContext) -> float:
        """Calculates instantaneous chemical hazard/oxidation rate."""
        R = 8.314
        temp_k = temp_c + 273.15
        try:
            return math.exp(-context.hazard_activation_energy / (R * temp_k)) * 1e8
        except OverflowError:
            return 1e10

    @classmethod
    def update_state(cls, 
                     current_state: TSRState, 
                     current_temp: float, 
                     dt: float, 
                     context: SafetyContext) -> TSRState:
        """
        Core logic to update risk state based on a new temperature reading.
        """
        # 1. Slope Analysis
        dt_slope = 0.0
        if current_state.last_temp is not None and dt > 0:
            dt_slope = (current_temp - current_state.last_temp) / dt
        
        # 2. Cumulative Damage (Chemical Aging)
        hazard = cls.calculate_hazard(current_temp, context)
        current_state.cumulative_risk += hazard * dt
        current_state.degradation_index = min(1.0, current_state.cumulative_risk / 5000)
        current_state.peak_slope = max(current_state.peak_slope, dt_slope)
        
        # 3. Predictive Time to Critical (PTC)
        if dt_slope > 0:
            current_state.safe_time_remaining = (context.critical_threshold_temp - current_temp) / dt_slope
        else:
            current_state.safe_time_remaining = 999.0
            
        # 4. Status Determination
        if current_temp >= context.critical_threshold_temp or current_state.degradation_index > 0.95:
            current_state.risk_level = "SHUTDOWN"
        elif current_state.safe_time_remaining < context.critical_buffer_seconds or current_state.degradation_index > 0.7:
            current_state.risk_level = "CRITICAL"
        elif current_state.safe_time_remaining < context.warning_buffer_seconds or current_state.degradation_index > 0.4:
            current_state.risk_level = "WARNING"
        else:
            current_state.risk_level = "SAFE"
            
        current_state.last_temp = current_temp
        return current_state
