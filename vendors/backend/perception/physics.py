import time
import math
from typing import Dict

class PhysicsEstimator:
    """
    [Food Physics Compiler Runtime]
    Converts raw TSV (Temperature, Time) into High-Level Physics Metrics (Maillard, etc).
    """
    
    MAILLARD_THRESHOLD = 140.0 # degC
    MAILLARD_RATE_CONST = 0.001 # Tuning parameter for "Browning per second at 150C"
    
    def __init__(self):
        self.maillard_accumulator = 0.0
        self.last_time = time.time()
        
    def process(self, tsv: Dict[str, float]) -> Dict[str, float]:
        """
        Update estimations based on latest TSV.
        """
        now = time.time()
        dt = now - self.last_time
        if dt <= 0: dt = 0.001
        
        current_temp = tsv.get("temp", 25.0)
        
        # 1. Maillard Reaction Rate (Simplified Arrhenius)
        # Reaction starts > 140C. Rate doubles every ~10C (Rule of Thumb).
        # Rate = k * 2^((T - 140)/10)
        rate = 0.0
        if current_temp > self.MAILLARD_THRESHOLD:
            over_temp = current_temp - self.MAILLARD_THRESHOLD
            # Avoid explosion
            if over_temp > 100: over_temp = 100 
            
            # Simple exponential growth of reaction rate
            rate = self.MAILLARD_RATE_CONST * (1.5 ** (over_temp / 10.0))
            
        self.maillard_accumulator += rate * dt
        
        self.last_time = now
        
        return {
            "maillard_index": round(self.maillard_accumulator, 4),
            "maillard_rate": round(rate, 5)
        }
        
    def reset(self):
        self.maillard_accumulator = 0.0
        self.last_time = time.time()
