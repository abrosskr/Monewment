import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.fis_physics import FisPhysics, PhysicsReactor

def test_dynamic_addition_thermal_mixing():
    print("\n🍵 Testing Dynamic Ingredient Addition: Thermal Mixing...")
    
    # 1. 500g Boiling Water (100C)
    reactor = PhysicsReactor(
        ingredients={"water": 500.0},
        current_temp=100.0
    )
    
    print(f"   Initial: 500g Water at {reactor.current_temp}C")
    
    # 2. Add 200g Cold Onion (4C)
    print("   Action: Adding 200g Cold Onion (4C)...")
    reactor = FisPhysics.add_ingredient(reactor, "onion", 200.0, temp_c=4.0)
    
    print(f"   Result: {reactor.total_mass_g}g mixture at {reactor.current_temp:.2f}C")
    
    # Theoretical Check: (500*4.18*100 + 200*3.8*4) / (500*4.18 + 200*3.8) = ~74.2C
    assert 70.0 < reactor.current_temp < 80.0
    print("   ✅ Thermal Mixing logic confirmed.")

def test_moisture_maillard_paradox():
    print("\n🥓 Testing Moisture-Maillard Paradox: Bell Curve Correction...")
    
    # High moisture scenario (aw ~ 0.9)
    wet_reactor = PhysicsReactor(ingredients={"beef": 100.0, "water": 900.0}, current_temp=154.0)
    # Optimal moisture scenario (aw ~ 0.6)
    opt_reactor = PhysicsReactor(ingredients={"beef": 100.0, "water": 150.0}, current_temp=154.0)
    
    dt = 10.0
    wet_reactor = FisPhysics.step_simulation(wet_reactor, dt)
    opt_reactor = FisPhysics.step_simulation(opt_reactor, dt)
    
    print(f"   Wet Progress (aw~0.9): {wet_reactor.reaction_progress['MAILLARD']:.6f}")
    print(f"   Opt Progress (aw~0.6): {opt_reactor.reaction_progress['MAILLARD']:.6f}")
    
    assert opt_reactor.reaction_progress['MAILLARD'] > wet_reactor.reaction_progress['MAILLARD']
    print("   ✅ Paradox Solved: Maillard reaction is inhibited by excessive moisture.")

if __name__ == "__main__":
    test_dynamic_addition_thermal_mixing()
    test_moisture_maillard_paradox()
