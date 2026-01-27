import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.vpt.core import VPTSimulator, VPTScenario, TimelineEvent

def test_vpt_scenario_complex_cooking():
    print("\n🏗️ Testing VPT Scenario: Realistic Beef Stew (Multiple Events)...")
    
    # Define Scenario
    scenario = VPTScenario(
        name="Beef Stew - Stage 1 (Searing & Water addition)",
        hardware_id="induction_01",
        initial_ingredients={"beef": 300.0},
        timeline=[
            TimelineEvent(time_s=0.0, action="SET_POWER", value=2000),   # Start Searing
            TimelineEvent(time_s=60.0, action="ADD_INGREDIENT", value={"name": "onion", "mass": 100.0, "temp": 23.0}),
            TimelineEvent(time_s=120.0, action="ADD_INGREDIENT", value={"name": "water", "mass": 500.0, "temp": 23.0}), # Water Lock Start
            TimelineEvent(time_s=130.0, action="SET_POWER", value=1500), # Lower heat for simmering
            TimelineEvent(time_s=300.0, action="CHANGE_AMBIENT", value=35.0) # Summer Kitchen scenario
        ],
        max_duration_s=400
    )
    
    vpt = VPTSimulator(scenario)
    history = vpt.run(dt=1.0)
    
    # Validate
    # 1. At 60s, temp should be high (searing)
    state_60s = next(h for h in history if h["time"] == 60)
    print(f"   Check at 60s: Temp = {state_60s['true_temp']:.2f}C")
    assert state_60s["true_temp"] > 100.0
    
    # 2. After 120s, temp should drop and lock near 100C due to water
    state_200s = next(h for h in history if h["time"] == 200)
    print(f"   Check at 200s: Temp = {state_200s['true_temp']:.2f}C (Water Lock)")
    assert 99.0 <= state_200s["true_temp"] <= 101.0
    
    print("\n   ✅ VPT Orchestration Successful: Multi-stage physics validated.")

if __name__ == "__main__":
    test_vpt_scenario_complex_cooking()
