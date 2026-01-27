import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.fis_physics import FisPhysics, CalibrationContext

def test_feedback_loop_efficiency():
    print("\n🔄 Testing Feedback Loop: Thermal Efficiency...")
    
    # 1. Initial State (Clean DB)
    mass = 550.0 # 550g
    delta_t = 80 # 20C -> 100C
    predicted_time = FisPhysics.calculate_cooking_duration(mass, 4.18, delta_t)
    print(f"   [Prediction 1] Time to boil 550g: {predicted_time}s")
    
    # 2. Simulate Sensor Feedback (Observation)
    # Actually took 20% longer (e.g. power grid fluctuation or old induction)
    actual_time = predicted_time * 1.2
    print(f"   [Observation ] Actually took: {actual_time}s (20% slower)")
    
    # 3. Create Calibration Context
    obs = {"actual_duration": actual_time}
    pred = {"predicted_duration": predicted_time}
    cal_context = FisPhysics.calibrate_from_sensor(pred, obs)
    print(f"   [Calibration ] Efficiency Multiplier: {cal_context.efficiency_multiplier}")
    
    # 4. Predict for a new task with Calibrated Context
    new_mass = 1000.0 # 1kg
    calibrated_time = FisPhysics.calculate_cooking_duration(new_mass, 4.18, delta_t, cal=cal_context)
    standard_time = FisPhysics.calculate_cooking_duration(new_mass, 4.18, delta_t)
    
    print(f"   [Prediction 2] Time to boil 1kg (Standard): {standard_time}s")
    print(f"   [Prediction 2] Time to boil 1kg (Calibrated): {calibrated_time}s")
    
    assert calibrated_time > standard_time
    print("   ✅ Efficiency Calibration Successful.")

def test_feedback_loop_ingredient_diffusivity():
    print("\n🥩 Testing Feedback Loop: Ingredient Diffusivity (Texture)...")
    
    # 1. Predict internal temp for 60s sear
    ing = ["beef"]
    initial_pred = FisPhysics.get_target_temp("sear", ing, duration=60)
    print(f"   [Prediction 1] Surface: {initial_pred['surface_temp']}C, Predicted Core: {initial_pred['core_temp_estimate']}C")
    
    # 2. Simulate Sensor (e.g. Internal Probe reading)
    # Actual core is much hotter (maybe the meat was thinner or more conductive)
    actual_core = initial_pred['core_temp_estimate'] + 15.0
    print(f"   [Observation ] Actual Core Temp: {actual_core}C (+15C error)")
    
    # 3. Calibrate
    obs = {"actual_core_temp": actual_core}
    pred = {"predicted_core_temp": initial_pred['core_temp_estimate'], "ingredients": ["beef"]}
    cal_context = FisPhysics.calibrate_from_sensor(pred, obs)
    print(f"   [Calibration ] Beef Diffusivity Offset: {cal_context.ingredient_offsets['beef']['diffusivity']}")
    
    # 4. Re-predict for another 60s
    calibrated_pred = FisPhysics.get_target_temp("sear", ing, duration=60, cal=cal_context)
    
    print(f"   [Standard Lag  ] Core: {initial_pred['core_temp_estimate']}C")
    print(f"   [Calibrated Lag] Core: {calibrated_pred['core_temp_estimate']}C")
    
    assert calibrated_pred['core_temp_estimate'] > initial_pred['core_temp_estimate']
    print("   ✅ Diffusivity Calibration Successful.")
    print("   ✅ Diffusivity Calibration Successful.")

if __name__ == "__main__":
    try:
        test_feedback_loop_efficiency()
        test_feedback_loop_ingredient_diffusivity()
        print("\n🏆 ALL SELF-CALIBRATION TESTS PASSED.")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
