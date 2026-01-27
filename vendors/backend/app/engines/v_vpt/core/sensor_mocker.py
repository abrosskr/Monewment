import random
import time
from typing import Dict, Any, List
from pydantic import BaseModel

class SensorNoiseConfig(BaseModel):
    temp_noise_sd: float = 0.5   # Standard deviation for Gaussian noise
    weight_noise_sd: float = 1.0
    latency_ms: int = 200        # Communication delay
    drift_rate: float = 0.0001   # Sensor drift over time

class VPTSensorMocker:
    """
    [VPT Sensor Mocker]
    Injects realistic noise, latency, and drift into simulation data.
    Ensures that engines are robust against imperfect real-world inputs.
    """
    
    @staticmethod
    def apply_noise(value: float, sd: float, drift: float = 0.0, elapsed_time: float = 0.0) -> float:
        """Adds Gaussian noise and time-based drift."""
        noise = random.normalvariate(0, sd)
        total_drift = drift * elapsed_time
        return value + noise + total_drift

    @classmethod
    def mock_reactor_state(cls, state_dict: Dict[str, Any], config: SensorNoiseConfig, elapsed_s: float) -> Dict[str, Any]:
        """Provides a 'noisy' view of the current reactor state."""
        # Simulated latency
        # In a real async test, we would sleep or delay current_temp update
        
        mocked = state_dict.copy()
        if "current_temp" in mocked:
            mocked["current_temp"] = cls.apply_noise(mocked["current_temp"], config.temp_noise_sd, config.drift_rate, elapsed_s)
        
        if "total_mass_g" in mocked:
            mocked["total_mass_g"] = cls.apply_noise(mocked["total_mass_g"], config.weight_noise_sd, config.drift_rate, elapsed_s)
            
        return mocked
