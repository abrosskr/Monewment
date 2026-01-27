import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.engines.v_bridge.core import VBridgeEngine, PhysicalStateTarget

def test_v_bridge_adaptation():
    print("\n🌉 Testing V-Bridge: Absolute Goal to Machine Command Adaptation")
    print("-" * 80)

    # The Absolute Goal: Reach 160C Surface and input 1200J/s Energy
    absolute_goal = PhysicalStateTarget(
        time_s=60.0,
        surface_temp_target=160.0,
        internal_energy_flux=1200.0,
        target_reaction_intensity=0.1,
        moisture_activity_limit=0.9
    )

    current_state = {"temp": 120.0, "mass": 500.0}

    # Case 1: High-end Profession Induction (90% Efficient)
    cmd_high = VBridgeEngine.translate_goal_to_command(
        absolute_goal, current_state, hardware_eff=0.9, material_sh=4.18
    )

    # Case 2: Old Camping Stove (40% Efficient)
    cmd_low = VBridgeEngine.translate_goal_to_command(
        absolute_goal, current_state, hardware_eff=0.4, material_sh=4.18
    )

    print(f"   [Absolute Goal] Surface: {absolute_goal.surface_temp_target}C, Flux: {absolute_goal.internal_energy_flux}J/s")
    print(f"   [Adaptation 1] Pro Induction (90% Eff) -> Power: {cmd_high['power']:.2f}W")
    print(f"   [Adaptation 2] Old Stove     (40% Eff) -> Power: {cmd_low['power']:.2f}W")

    # The old stove needs much more power to achieve the SAME physical flux
    assert cmd_low['power'] > cmd_high['power']
    print("\n   ✅ SUCCESS: V-Bridge translated the same physical goal into different machine commands.")

if __name__ == "__main__":
    test_v_bridge_adaptation()
