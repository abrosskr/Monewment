import logging
import numpy as np
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class DualSensorCalibrationService:
    """
    [Grand Fortification: Sensor Redundancy]
    Ensures 'Single Source of Truth' by cross-validating redundant sensors.
    Supports Bayesian Estimation by providing high-confidence inputs.
    """

    # Tolerance for sensor drift 
    DRIFT_TOLERANCE_PCT = 0.05 # 5% max deviation between dual sensors

    def __init__(self):
        self.calibration_offset = 0.0
        self.is_healthy = True
        self.confidence_score = 1.0

    def validate_and_fuse(self, primary_reading: float, secondary_reading: float) -> Tuple[float, float]:
        """
        Cross-validates primary (e.g. Probe) vs secondary (e.g. IR/Acoustic).
        Returns (FusedReading, Confidence).
        """
        deviation = abs(primary_reading - secondary_reading)
        avg = (primary_reading + secondary_reading) / 2
        
        # Check for catastrophic drift (Sensor failure detection)
        if (deviation / (avg if avg != 0 else 1)) > self.DRIFT_TOLERANCE_PCT:
            self.is_healthy = False
            self.confidence_score = 0.4
            logger.warning(f"⚠️ SENSOR DRIFT DETECTED: Primary({primary_reading}) vs Secondary({secondary_reading}). Deviation > {self.DRIFT_TOLERANCE_PCT*100}%")
            # In Grand Fortification, we prioritize the safer (highest) reading for temp
            fused = max(primary_reading, secondary_reading)
        else:
            self.is_healthy = True
            self.confidence_score = 1.0 - (deviation / (avg if avg != 0 else 1))
            fused = avg

        return fused, self.confidence_score

    def calibrate_base(self, ambient_reading: float, reference_temp: float = 25.0):
        """
        Resets baseline offset at start of session.
        """
        self.calibration_offset = reference_temp - ambient_reading
        logger.info(f"⚖️ Sensor Baseline Calibrated. Offset: {self.calibration_offset}C")

    def get_status(self) -> Dict:
        return {
            "is_healthy": self.is_healthy,
            "confidence": self.confidence_score,
            "offset": self.calibration_offset
        }
