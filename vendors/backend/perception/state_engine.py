import numpy as np
from collections import deque
import time
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Try importing scipy for robust differentiation
try:
    from scipy.signal import savgol_filter
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    logger.warning("Scipy not found. Using simple gradient fallback.")

class StateVectorEngine:
    """
    [The Brain of Phase 2]
    Converts raw Stream -> Thermal State Vector (TSV).
    TSV = [T, T', T'', Integral, Time_since_Event]
    """
    
    def __init__(self, window_size: int = 15, poly_order: int = 2):
        """
        Args:
            window_size: Number of samples to keep (10Hz * 1.5s = 15)
            poly_order: Polynomial order for Savitzky-Golay (2 or 3)
        """
        self.window_size = window_size
        self.poly_order = poly_order
        
        # Buffer: Stores (timestamp, temperature)
        self.history = deque(maxlen=window_size)
        
        # Internal State
        self.integral_sum = 0.0
        self.last_event_time = time.time()
        self.base_temp_threshold = 50.0 # Integrate heat above this (e.g. 50C)
        
        # Tuning for Event Detection
        self.accel_threshold = 2.0 # deg/s^2 (Sudden change)

    def process_reading(self, timestamp: float, temp: float) -> Dict[str, float]:
        """
        Ingest a new reading and return the current TSV.
        """
        # 0. Input Sanitization
        if np.isnan(temp) or np.isinf(temp):
            logger.warning("Invalid Temp (NaN/Inf) detected. Skipping.")
            return self._last_valid_tsv if hasattr(self, '_last_valid_tsv') else {
                "temp": 0.0, "velocity": 0.0, "acceleration": 0.0, "integral": 0.0, "time_since_event": 0.0
            }
            
        dt = 0.1 # Default if mostly 10Hz
        if len(self.history) > 0:
            dt = timestamp - self.history[-1][0]
            if dt <= 0: dt = 0.001 # Fix duplicates
            
        self.history.append((timestamp, temp))
        
        # 1. Integral Calculation (Simple Trapezoidal)
        if temp > self.base_temp_threshold:
            self.integral_sum += (temp - self.base_temp_threshold) * dt

        # 2. Derivative Calculation
        velocity = 0.0      # dT/dt
        acceleration = 0.0  # d2T/dt2
        
        if len(self.history) >= self.window_size:
            temps = np.array([x[1] for x in self.history])
            
            # Robust Scipy Usage with Fallback
            computed = False
            if HAS_SCIPY:
                try:
                    # Estimate average sampling rate of the window
                    times = np.array([x[0] for x in self.history])
                    avg_dt = np.mean(np.diff(times)) if len(times) > 1 else 0.1
                    if avg_dt <= 0.001: avg_dt = 0.001

                    vel_arr = savgol_filter(temps, window_length=self.window_size, polyorder=self.poly_order, deriv=1, delta=avg_dt)
                    acc_arr = savgol_filter(temps, window_length=self.window_size, polyorder=self.poly_order, deriv=2, delta=avg_dt)
                    
                    velocity = vel_arr[-1]
                    acceleration = acc_arr[-1]
                    computed = True
                except Exception as e:
                    logger.error(f"Scipy Math Error: {e}. Falling back to Gradient.")
                    computed = False
            
            if not computed:
                # Numpy Gradient Fallback (Noisier)
                times = np.array([x[0] for x in self.history])
                # Ensure times strictly increasing for gradient? 
                # np.gradient handles non-uniform but fails on duplicate x.
                # Simplified: Assume uniform if times are bad
                try:
                    grads = np.gradient(temps, times)
                    velocity = grads[-1]
                    acc_grads = np.gradient(grads, times)
                    acceleration = acc_grads[-1]
                except:
                    velocity = 0.0
                    acceleration = 0.0

        # 3. Event Detection (Reset Clock on Shock)
        # If acceleration spike is detected (e.g. cold meat hitting pan)
        if abs(acceleration) > self.accel_threshold:
            # Debounce: Only reset if it's been a while? 
            # For now, just mark current time
            self.last_event_time = timestamp

        time_since_event = timestamp - self.last_event_time
        
        return {
            "temp": round(temp, 2),
            "velocity": round(velocity, 4),
            "acceleration": round(acceleration, 4),
            "integral": round(self.integral_sum, 1),
            "time_since_event": round(time_since_event, 1)
        }

    def reset(self):
        self.history.clear()
        self.integral_sum = 0.0
        self.last_event_time = time.time()
