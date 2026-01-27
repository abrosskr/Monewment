import logging
import math
import time
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class ActuatorGovernor:
    """
    [Layer 0.5: Actuator Governor]
    The final gatekeeper before the physical burner.
    Enforces physical limits that the AI is not allowed to override.
    """
    
    def __init__(self, max_power_watts: float = 1500.0, max_slew_rate: float = 150.0):
        """
        Args:
            max_power_watts: Absolute hard limit (e.g. 1500W)
            max_slew_rate: Max Watts change per second (e.g. 150W/s = 10% per sec)
        """
        self.max_power = max_power_watts
        self.max_slew_rate = max_slew_rate
        
        self.last_watts = 0.0
        self.last_update_time = time.time()
        
    def govern(self, raw_watts: float, sensor_age: float, safety_lockout: bool = False) -> float:
        """
        Sanitize and limit the command.
        
        Args:
            raw_watts: The requested power from Navigator.
            sensor_age: Time since last valid sensor reading (seconds).
            safety_lockout: If True (e.g. Safety Engine Triggered), force 0.
        """
        now = time.time()
        dt = now - self.last_update_time
        if dt <= 0: dt = 0.001
        
        # 1. 🛑 Priority Check: Safety Lockout
        if safety_lockout:
            # logger.warning("Governor: Safety Lockout Active. Forcing 0W.") # Too noisy for high freq
            self.last_watts = 0.0
            self.last_update_time = now
            return 0.0

        # 2. 🛑 Priority Check: Sensor Age (Watchdog)
        if sensor_age > 1.0: # 1 Second Tolerance
            logger.critical(f"Governor: Sensor Stale ({sensor_age:.2f}s). Forcing 0W.")
            self.last_watts = 0.0
            self.last_update_time = now
            return 0.0

        # 3. 🛡️ Input Sanitization (NaN/Inf Protection)
        if math.isnan(raw_watts) or math.isinf(raw_watts):
            logger.error("Governor: Invalid Command (NaN/Inf). Forcing 0W.")
            self.last_watts = 0.0 # Reset on error
            self.last_update_time = now
            return 0.0
            
        # 4. 📉 Hard Clamping (range 0 ~ MAX)
        # Assuming Negative Watts = Active Cooling (not supported yet, so 0)
        clamped_watts = max(0.0, min(self.max_power, raw_watts))
        
        # 5. ⏳ Slew Rate Limiting (Soft Start / Soft Stop)
        # Prevents thermal shock and electrical surges
        max_change = self.max_slew_rate * dt
        
        delta = clamped_watts - self.last_watts
        
        # Clamp delta
        if delta > max_change:
            clamped_watts = self.last_watts + max_change
        elif delta < -max_change:
            clamped_watts = self.last_watts - max_change
            
        # 6. Final Update
        self.last_watts = clamped_watts
        self.last_update_time = now
        
        return float(clamped_watts)
        
    def reset(self):
        self.last_watts = 0.0
        self.last_update_time = time.time()
