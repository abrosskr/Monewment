import numpy as np
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.engines.v_calibration.core import VCalibrationEngine

def test_kalman_efficiency_recovery():
    print("\n🚀 Testing V-Kalman: Hardware Efficiency Recovery from Noisy Data")
    print("-" * 75)

    # Setup
    initial_temp = 23.0
    kf = VCalibrationEngine.initialize_filter(initial_temp)
    
    dt = 1.0
    power = 1500.0  # Watts
    thermal_mass = 500.0 # m*cp
    
    # GROUND TRUTH: The pan is actually 70% efficient
    true_eff = 0.7
    true_temp = initial_temp
    
    print(f"   [Config] True Efficiency: {true_eff*100}%, Model Start: 100.0%")
    print(f"   [Step]   True_T | Meas_T | Est_T | Est_Eff")
    
    for i in range(20):
        # 1. Physics Step (Ground Truth)
        true_temp += (power * true_eff * dt) / thermal_mass
        
        # 2. Sensor measurement (With Noise)
        noise = np.random.normal(0, 0.5)
        measured_temp = true_temp + noise
        
        # 3. Kalman Filter Step
        est_temp, est_eff = VCalibrationEngine.step_estimation(
            kf, dt, power, thermal_mass, measured_temp
        )
        
        if i % 2 == 0:
            print(f"   #{i:02d}    {true_temp:6.2f} | {measured_temp:6.2f} | {est_temp:6.2f} | {est_eff*100:6.2f}%")

    # Final Convergence Check
    print("-" * 75)
    print(f"   Final Estimated Efficiency: {est_eff*100:.2f}%")
    print(f"   Error: {abs(est_eff - true_eff)*100:.2f}%")
    
    assert abs(est_eff - true_eff) < 0.1 # Should converge within 10% in 20 steps
    print("\n   ✅ SUCCESS: Kalman Filter successfully decoupled noise from hardware inefficiency.")

if __name__ == "__main__":
    test_kalman_efficiency_recovery()
