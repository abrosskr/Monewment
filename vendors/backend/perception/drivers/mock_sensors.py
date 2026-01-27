import time
import math
import random
from app.perception.drivers.base_driver import BaseSensorDriver

class MockProbeDriver(BaseSensorDriver):
    """
    [Teacher Sensor 1]
    Simulates a Core Temperature Probe.
    Scenario: Steak cooking from 5C to 65C.
    """
    def __init__(self):
        self.start_time = time.time()
        self.initial_temp = 5.0
        self.target_temp = 65.0 # Medium Rare
        
    def connect(self):
        return True
        
    def read(self):
        elapsed = time.time() - self.start_time
        # Logistic curve simulation (S-curve)
        # T(t) = T_max / (1 + exp(-k(t-t0)))
        
        k = 0.05 # Heating rate
        progress = 1 - math.exp(-k * elapsed) # Simplified exponential approach
        
        current_temp = self.initial_temp + (self.target_temp - self.initial_temp) * progress
        noise = random.uniform(-0.5, 0.5) # Increased to match REAL AX8 Noise levels
        
        return {
            "timestamp": time.time(),
            "core_temp": round(current_temp + noise, 2),
            "device": "MOCK_PROBE_V1"
        }

    def close(self):
        pass

class MockScaleDriver(BaseSensorDriver):
    """
    [Teacher Sensor 2]
    Simulates a Smart Kitchen Scale.
    Scenario: Water evaporation (Mass Loss).
    """
    def __init__(self, initial_mass_g: float = 300.0):
        self.start_time = time.time()
        self.initial_mass = initial_mass_g
        self.evaporation_rate = 0.5 # g/sec (Simulated high heat)
        
    def connect(self):
        return True
        
    def read(self):
        elapsed = time.time() - self.start_time
        loss = self.evaporation_rate * elapsed
        current_mass = max(0, self.initial_mass - loss)
        
        noise = random.uniform(-0.5, 0.5) # Scale jitter
        
        return {
            "timestamp": time.time(),
            "mass_g": round(current_mass + noise, 1),
            "evaporation_rate": self.evaporation_rate,
            "device": "MOCK_SCALE_V1"
        }

    def close(self):
        pass
