import sys
import os
import time

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.fis_physics import FisPhysics, PhysicsReactor, CalibrationContext

def test_simulation_run():
    print("\n🚀 Starting Time-series Simulation: Boiling 500g Water...")
    
    # 1. Initialize Reactor
    reactor = PhysicsReactor(
        ingredients={"water": 500.0},
        current_temp=20.0, # Start from 20C
        cooking_method="BOILING"
    )
    
    # 2. Simulate for 300 seconds (5 minutes) in 10-second steps
    steps = 30
    dt = 10.0 # 10s steps
    
    print(f"   {'Time (s)':<10} | {'Temp (C)':<10} | {'Mass (g)':<10} | {'Maillard':<10}")
    print("-" * 55)
    
    for _ in range(steps):
        reactor = FisPhysics.step_simulation(reactor, dt, power_watts=1500)
        
        # Log every 50 seconds or when boiling
        if int(reactor.elapsed_time) % 50 == 0 or reactor.current_temp >= 100:
            print(f"   {reactor.elapsed_time:<10.1f} | {reactor.current_temp:<10.2f} | {reactor.total_mass_g:<10.1f} | {reactor.reaction_progress['MAILLARD']:<10.4f}")
        
        if reactor.elapsed_time > 300: break

    assert reactor.current_temp >= 99.0 # Should be at boiling point
    assert reactor.total_mass_g < 500.0 # Moisture should have evaporated
    print("\n   ✅ Simulation Complete: Water reached boiling and evaporated as expected.")

def test_high_heat_reaction_progression():
    print("\n🥩 Starting Time-series Simulation: Searing Meat (High Heat)...")
    
    reactor = PhysicsReactor(
        ingredients={"beef": 200.0},
        current_temp=154.0, # Assume already at Maillard threshold
        cooking_method="STIR_FRY"
    )
    
    dt = 1.0 # 1s steps for high precision
    duration = 60 # 60 seconds sear
    
    for _ in range(duration):
        reactor = FisPhysics.step_simulation(reactor, dt, power_watts=2000)
    
    print(f"   Final State after 60s Sear:")
    print(f"   - Temp: {reactor.current_temp:.2f}C")
    print(f"   - Maillard Progress: {reactor.reaction_progress['MAILLARD']:.4f}")
    print(f"   - Mass Remaining: {reactor.total_mass_g:.1f}g")
    
    assert reactor.reaction_progress['MAILLARD'] > 0.1
    print("\n   ✅ Reaction Progression Successful.")

if __name__ == "__main__":
    try:
        test_simulation_run()
        test_high_heat_reaction_progression()
        print("\n🏆 TIME-SERIES ENGINE VALIDATION PASSED.")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
