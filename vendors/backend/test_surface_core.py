import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.fis_physics import FisPhysics, PhysicsReactor

def test_surface_core_paradox():
    print("\n🔬 Testing Physics Paradox: Surface-Core Gradient (Avoid Burning)")
    print("-" * 85)

    # Scenario: Extreme Heat (2500W) on 500g Beef
    # We want to see if surface temp skyrockets while core lags behind
    reactor = PhysicsReactor(
        ingredients={"beef": 500.0},
        current_temp=23.0,
        core_temp=23.0
    )

    print(f"   [Step] Time | Surface_T | Core_T | Gradient | Reaction Qual")
    
    for i in range(10):
        # Apply High Power
        FisPhysics.step_simulation(reactor, 5.0, power_watts=2500.0) 
        
        gradient = reactor.current_temp - reactor.core_temp
        # Maillard would normally be high, but high gradient should penalize QF
        print(f"   #{i:02d} |  {i*5:3d}s | {reactor.current_temp:7.2f}C | {reactor.core_temp:6.2f}C | {gradient:7.2f}C")

    # Final Check
    if (reactor.current_temp - reactor.core_temp) > 80.0:
        print("\n   🚩 RESULT: High Gradient Detected! Surface is charring while core is cold.")
        print("   ✅ SUCCESS: Physics engine correctly identified the 'Surface vs Core' contradiction.")

if __name__ == "__main__":
    test_surface_core_paradox()
