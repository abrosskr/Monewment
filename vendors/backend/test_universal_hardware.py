import numpy as np
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.engines.v_calibration.core import VCalibrationEngine

def test_universal_hardware_kalman():
    print("\n🌐 Testing V-Kalman Universality: From Oven to Heavy Pot")
    print("-" * 80)

    # Context 1: Air Oven (Small thermal mass, fast response)
    # Context 2: Heavy Cast Iron Pot (Large thermal mass, slow response)
    
    scenarios = [
        {"name": "Smart Oven", "thermal_mass": 50.0, "power": 2000.0, "true_eff": 0.85},
        {"name": "Cast Iron Pot", "thermal_mass": 1200.0, "power": 1500.0, "true_eff": 0.65}
    ]

    for sc in scenarios:
        print(f"\n   [Scenario] System: {sc['name']}")
        print(f"   Target: Recover {sc['true_eff']*100}% Efficiency from Noisy Sensors.")
        
        kf = VCalibrationEngine.initialize_filter(23.0)
        true_temp = 23.0
        
        for i in range(15):
            # 1. Physics (Ground Truth)
            true_temp += (sc['power'] * sc['true_eff'] * 1.0) / sc['thermal_mass']
            
            # 2. Noisy Measurement
            measured_temp = true_temp + np.random.normal(0, 0.5)
            
            # 3. Kalman Recovery
            est_temp, est_eff = VCalibrationEngine.step_estimation(
                kf, 1.0, sc['power'], sc['thermal_mass'], measured_temp
            )
            
            if i % 3 == 0:
                print(f"      Step {i:02d}: Measured {measured_temp:6.2f}C | Estimated Eff: {est_eff*100:6.2f}%")
        
        error = abs(est_eff - sc['true_eff'])
        print(f"   >>> Result: Final Est Eff for {sc['name']}: {est_eff*100:.2f}% (Error: {error*100:.2f}%)")
        assert error < 0.15

    print("\n   ✅ CONCLUSION: Same Kalman logic handles both Air and Metal systems.")

if __name__ == "__main__":
    test_universal_hardware_kalman()
