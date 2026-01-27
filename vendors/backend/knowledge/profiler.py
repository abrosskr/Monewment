import numpy as np
import logging
from typing import List, Dict, Optional
from datetime import datetime
from app.models.pan import PanProfile

logger = logging.getLogger(__name__)

class PanProfiler:
    """
    [System Identification Engine]
    Extracts physical parameters (mc, hA) from TSV history.
    
    Physics Model:
    mc * dT/dt = Qin - hA * (T - T_amb)
    """
    
    def __init__(self):
        self.t_amb = 25.0 # Ambient Temp Assumption
        self.estimated_input_power = 1500.0 # Watts (Induction Max) - Needs calibration too?
        
    def analyze_calibration_run(self, 
                                pan_name: str, 
                                tsv_history: List[Dict[str, float]]) -> PanProfile:
        """
        Input: a list of TSV dicts [{'temp':..., 'velocity':..., 'timestamp':...}]
        recording a full Heat-up & Cool-down cycle.
        """
        if not tsv_history:
            raise ValueError("Empty history")
            
        # 1. Segment Data: Heating vs Cooling
        # Simple logic: If Power was ON (assumed start) vs OFF (assumed end)
        # Or just use velocity sign.
        # But cooling phase is cleaner for hA.
        
        times = np.array([x['timestamp'] for x in tsv_history])
        temps = np.array([x['temp'] for x in tsv_history])
        vels  = np.array([x['velocity'] for x in tsv_history])
        
        # Find peak temp index
        peak_idx = np.argmax(temps)
        
        # Heating Phase: 0 to peak
        # Cooling Phase: peak to end
        cooling_slice = slice(peak_idx + 10, len(temps)) # Skip transition logic
        
        # 2. Identify hA (Heat Loss Coefficient) from Cooling
        # Equation: mc * dT/dt = -hA * (T - T_amb)  (Qin=0)
        # => dT/dt / (T - T_amb) = -hA / mc = -k_cool (Cooling Constant)
        
        t_cool = temps[cooling_slice]
        v_cool = vels[cooling_slice]
        
        valid_mask = (t_cool > self.t_amb + 10) # Filter near ambient noise
        if not np.any(valid_mask):
             logger.warning("Not enough cooling data. Using default.")
             k_cool = 0.01
        else:
             # v = -k * (T - Tamb)
             # k = -v / (T - Tamb)
             # Robust fit: Polyfit(T-Tamb, -v, 1) -> slope is k_cool
             delta_T = t_cool[valid_mask] - self.t_amb
             neg_vel = -v_cool[valid_mask]
             
             # Force intercept through zero? Or standard linear regression
             # Let's do simple average of ratio for now or Least Squares
             # k_cool = np.mean(neg_vel / delta_T) 
             slope, _ = np.polyfit(delta_T, neg_vel, 1)
             k_cool = max(0.001, slope)
             
        # 3. Identify mc (Thermal Mass) from Heating
        # Equation: Qin = mc * dT/dt + hA * (T - T_amb)
        # => mc = (Qin - hA(T-Tamb)) / (dT/dt)
        # Reliability: Use the linear part of heating where dT/dt is stable high.
        
        heating_slice = slice(0, peak_idx)
        t_heat = temps[heating_slice]
        v_heat = vels[heating_slice]
        
        # Select region where Velocity is high and stable (e.g., > 1.0 C/s)
        fast_heat_mask = (v_heat > 1.0)
        
        if not np.any(fast_heat_mask):
            mc_estimate = 500.0 # Default fallback
        else:
            # We don't know hA yet strictly in units, but k_cool = hA/mc
            # so hA = k_cool * mc
            # Qin = mc * v + k_cool * mc * (T - Tamb)
            # Qin = mc * [ v + k_cool * (T - Tamb) ]
            # mc = Qin / [ v + k_cool * (T - Tamb) ]
            
            denom = v_heat[fast_heat_mask] + k_cool * (t_heat[fast_heat_mask] - self.t_amb)
            mc_values = self.estimated_input_power / denom
            mc_estimate = np.median(mc_values)
            
        # 4. Calculate final hA
        hA_estimate = k_cool * mc_estimate
        
        return PanProfile(
            id=f"PAN_{int(datetime.utcnow().timestamp())}",
            name=pan_name,
            diameter_cm=28.0, # User input usually, default for now
            material_type="Detected_Metal",
            thermal_mass=round(mc_estimate, 1),
            heat_loss_coeff=round(hA_estimate, 3),
            calibration_date=datetime.utcnow()
        )
