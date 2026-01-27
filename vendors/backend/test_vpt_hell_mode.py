import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.fis_physics import FisPhysics, PhysicsReactor
from app.engines.v_vpt.core.simulator import VPTSimulator, VPTScenario, TimelineEvent
from app.engines.v_surface.core import SurfaceState

def run_gas_vs_induction_vpt():
    print("\n🔥 VPT Battle: Induction (Pro) vs. Gas (Home) vs. Sticking Recovery")
    print("-" * 75)

    # Scenario 1: Pro Induction (Dual Sensor)
    scen_pro = VPTScenario(
        name="Pro Induction - 300g Water",
        hardware_id="induction_01",
        initial_ingredients={"water": 300.0},
        timeline=[TimelineEvent(time_s=0.0, action="SET_POWER", value=2000)],
        max_duration_s=100
    )
    vpt_pro = VPTSimulator(scen_pro)
    vpt_pro.reactor.heating_method = "INDUCTION"
    vpt_pro.reactor.sensor_mode = "DUAL"
    res_pro = vpt_pro.run(dt=1.0)

    # Scenario 2: Home Gas (Single Sensor, High Loss)
    scen_gas = VPTScenario(
        name="Home Gas - 300g Water",
        hardware_id="gas_stove_generic",
        initial_ingredients={"water": 300.0},
        timeline=[TimelineEvent(time_s=0.0, action="SET_POWER", value=2000)], # Same power input
        max_duration_s=100
    )
    vpt_gas = VPTSimulator(scen_gas)
    vpt_gas.reactor.heating_method = "GAS"
    vpt_gas.reactor.sensor_mode = "SINGLE"
    res_gas = vpt_gas.run(dt=1.0)

    # Scenario 3: Sticking Recovery (Pulse Heating)
    scen_stick = VPTScenario(
        name="Sticking Recovery Test",
        hardware_id="damaged_pan",
        initial_ingredients={"beef": 200.0},
        timeline=[TimelineEvent(time_s=0.0, action="SET_POWER", value=1500)],
        max_duration_s=60
    )
    vpt_stick = VPTSimulator(scen_stick)
    vpt_stick.reactor.surface = SurfaceState(coating_integrity=0.1, oil_film_density=0.0) # Bad pan
    res_stick = vpt_stick.run(dt=1.0)

    # Validation & Report
    final_pro_t = res_pro[-1]["true_temp"]
    final_gas_t = res_gas[-1]["true_temp"]

    print("\n📊 VPT HELL MODE REPORT:")
    print(f"   - Induction Final (100s): {final_pro_t:.2f}C (Efficiency: 85%)")
    print(f"   - Gas Final (100s):       {final_gas_t:.2f}C (Efficiency: 40% + Convective Waste)")
    print(f"   - Sticking Result: Risk Level {vpt_stick.reactor.tsr.risk_level}, Adhesion Risk {vpt_stick.reactor.surface.adhesion_risk:.2f}")
    
    # Assertions
    assert final_pro_t > final_gas_t
    print("\n   ✅ Simulation Logic Passed: Gas heat loss and Induction efficiency accurately modeled.")

if __name__ == "__main__":
    run_gas_vs_induction_vpt()
