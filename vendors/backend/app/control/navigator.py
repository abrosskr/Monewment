import logging
from typing import Dict, Any
from app.models.pan import PanProfile

logger = logging.getLogger(__name__)

class Navigator:
    """
    [V5.2 Adaptive Feedforward Control]
    Calculates the required energy input to track a Golden Trajectory.
    
    Physics Model (Inverse Dynamics):
    Required_Power% = (Target_Velocity + Cooling_Loss_Compensation) / Max_Heating_Capacity
    u = (v_ref + beta * (T - T_amb)) / alpha
    """
    def __init__(self):
        self.p_max = 1500.0 # Watts (Induction Max Reference)
        self.t_amb = 25.0
        
        # PID Gains (Acting on Velocity Error K/s)
        self.kp = 0.5 
        self.ki = 0.1
        self.kd = 0.1
        
        self.accumulated_error = 0.0
        self.last_error = 0.0
        self.dt = 0.1 # assumed 10Hz control loop

    def reset(self):
        self.accumulated_error = 0.0
        self.last_error = 0.0

    def calculate_action(self, 
                         current_tsv: Dict[str, float], 
                         target_tsv: Dict[str, float], 
                         station: PanProfile) -> Dict[str, float]:
        """
        Returns:
            {
                "power_ratio": 0.0 ~ 1.0 (Control Signal),
                "debug_info": ...
            }
        """
    def calculate_action(self, 
                         current_tsv: Dict[str, float], 
                         target_tsv: Dict[str, float], 
                         station: PanProfile) -> Dict[str, float]:
        """
        Returns:
            {
                "power_ratio": 0.0 ~ 1.0 (Control Signal),
                "cmd_watts": float,
                ...
            }
        """
        # Pure Control Logic
        # Safety is now handled by SafetyEngine & Governor outside this class.

        # 1. Extract Station Physics
        mc = station.thermal_mass if station.thermal_mass > 100.0 else 500.0
        hA = station.heat_loss_coeff if station.heat_loss_coeff > 0.1 else 5.0
        
        # Anti-Singularity: Ensure alpha is never zero or too small
        alpha = self.p_max / mc
        alpha = max(alpha, 0.1) # Min acceleration 0.1 K/s
        
        beta = hA / mc
        
        # 2. Feedforward Control (Inverse Dynamics)
        v_ref = target_tsv.get('velocity', 0.0)
        temp_curr = current_tsv.get('temp', 25.0)
        
        delta_T = temp_curr - self.t_amb
        loss_compensation = beta * delta_T 
        
        u_ff = (v_ref + loss_compensation) / alpha
        
        # 3. Feedback Control (PID)
        v_curr = current_tsv.get('velocity', 0.0)
        error_v = v_ref - v_curr
        
        # --- 🛡️ SAFETY CHECK 3: DERIVATIVE FILTERING 🛡️ ---
        # Don't trust raw derivative. Use simple bounded diff.
        raw_derivative = (error_v - self.last_error) / self.dt
        # Simple clamp to prevent noise spikes
        derivative_error = max(-5.0, min(5.0, raw_derivative)) 
        
        # PID Calc
        p_term = self.kp * error_v
        i_term = self.ki * self.accumulated_error
        d_term = self.kd * derivative_error
        
        v_correction = p_term + i_term + d_term
        u_fb = v_correction / alpha
        
        # 4. Final Control Signal & Clamping
        u_total = u_ff + u_fb
        # 4. Final Control Signal
        u_total = u_ff + u_fb
        
        # Navigator asks for what it WANTS.
        # Governor decides what it GETS.
        # However, for Anti-Windup, we still need to know if we are pushing limits.
        # Ideally we'd get feedback. For now, we clamp simply to range [0, 1] for Integral Logic.
        
        u_clamped_pid = max(0.0, min(1.0, u_total))
        
        # --- 🛡️ SAFETY CHECK 4: ANTI-WINDUP 🛡️ ---
        # Only accumulate Integral if output is not saturated
        is_saturated_high = (u_clamped_pid == 1.0)
        is_saturated_low = (u_clamped_pid == 0.0)
        
        if (is_saturated_high and error_v > 0) or (is_saturated_low and error_v < 0):
             pass # Stop integration
        else:
             self.accumulated_error += error_v * self.dt
             
        self.last_error = error_v
        
        cmd_watts = u_clamped_pid * self.p_max
        
        return {
            "power_ratio": float(u_clamped_pid),
            "cmd_watts": float(cmd_watts),
            "components": {
                "ff": float(u_ff),
                "fb": float(u_fb),
                "cooling_comp": float(loss_compensation / alpha)
            },
            "physics": {
                "alpha": float(alpha),
                "beta": float(beta),
                "error_v": float(error_v)
            }
        }
