import logging
import time
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class SafetyEngine:
    """
    [Layer 1: Safety Rules Engine]
    Monitors TSV and System State.
    Returns (is_safe, reason).
    Decoupled from Control Logic.
    """
    
    def __init__(self):
        self.max_temp = 280.0 # Celsius (Flashpoint protection)
        self.liftoff_threshold = -5.0 # K/s (Sudden cooling)
        
    def evaluate(self, tsv: Dict[str, float]) -> Tuple[bool, str]:
        """
        Check if the current state is safe for operation.
        Returns: (Safe: bool, Reason: str)
        """
        now = time.time()
        
        # 1. Thermal Limit Check
        temp = tsv.get('temp', 0.0)
        if temp > self.max_temp:
            return False, f"OVERHEAT ({temp:.1f} > {self.max_temp})"
            
        # 2. Pan Liftoff Detection
        # If velocity is negative and large (cooling very fast), pan is likely gone
        # or sensor is seeing background.
        velocity = tsv.get('velocity', 0.0)
        if velocity < self.liftoff_threshold:
            # But wait, maybe we ARE cooling down intentionally?
            # Usually heavy pans don't cool at -5 K/s naturally unless quenched.
            # Air cooling is ~ -0.1 to -0.5 K/s.
            return False, f"LIFTOFF DETECTED (v={velocity:.1f})"
            
        # 3. Invalid State
        if tsv.get('velocity') == 0.0 and tsv.get('acceleration') == 0.0 and tsv.get('integral') == 0.0:
            # State engine returns all zeros on NaN/Error.
            # If temp is also 0 (and not cold start), suspicious.
            if temp == 0.0:
                 return False, "INVALID_STATE_ZERO"

        return True, "OK"
