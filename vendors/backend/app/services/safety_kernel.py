import logging
import time
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class EmergencyStopService:
    """
    [Grand Fortification: Safety Kernel]
    Isolated hardware-linked safety monitor. 
    Triggers 'Emergency Stop' (ESTOP) if physical constraints are violated.
    Logic is independent of AI optimization to prevent 'Reward Hacking'.
    """

    # Physical Constants for Safety
    MAX_ALLOWABLE_TEMP = 235.0  # Celsius (Immediate carbonization/fire risk)
    MAX_THERMAL_GRADIENT = 85.0 # Celsius (Difference between surface and core)
    RAPID_MELT_THRESHOLD = 50.0 # Rate of change per 10s for frozen items

    def __init__(self):
        self.is_estop_active = False
        self.last_fault_reason = ""
        self.stop_signal_timestamp = None

    def check_constraints(self, surface_temp: float, core_temp: float, state: str = "ROOM_TEMP") -> bool:
        """
        Performs high-frequency safety check. 
        Returns True if SAFE, False if ESTOP triggered.
        """
        if self.is_estop_active:
            return False

        # 1. Absolute Maximum Temperature Check
        if surface_temp > self.MAX_ALLOWABLE_TEMP:
            return self._trigger_estop(f"OVERHEAT: Surface temp {surface_temp}C exceeds MAX {self.MAX_ALLOWABLE_TEMP}C")

        # 2. Thermal Gradient Check (Prevent raw core / burnt surface)
        gradient = abs(surface_temp - core_temp)
        if gradient > self.MAX_THERMAL_GRADIENT:
            return self._trigger_estop(f"GRADIENT_VIOLATION: Alpha-Beta delta {gradient}C exceeds threshold {self.MAX_THERMAL_GRADIENT}C")

        # 3. Industrial Health Safety: Frozen Pathogen Check
        if state == "FROZEN" and core_temp < -2.0 and surface_temp > 100.0:
            # RL might try to flash-sear frozen items, leaving the core in a pathogen-growth room-temp zone
            # while the surface is carbonizing.
             return self._trigger_estop("FROZEN_FLASH_SEAR_REJECT: High risk of surface carbonization with ice core.")

        return True

    def _trigger_estop(self, reason: str) -> bool:
        self.is_estop_active = True
        self.last_fault_reason = reason
        self.stop_signal_timestamp = time.time()
        logger.critical(f"🛑 EMERGENCY STOP TRIGGERED: {reason}")
        # In a real scenario, this would call a GPIO pin or hardware interrupt
        return False

    def reset_estop(self):
        """Manual reset required as per safety protocol."""
        self.is_estop_active = False
        self.last_fault_reason = ""
        logger.info("🛡️ Emergency Stop System Reset. Safety Kernel Standby.")
