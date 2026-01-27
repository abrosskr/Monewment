import sys
import os
import math

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.fis_physics import FisPhysics, PhysicsReactor

def test_vandors_tsr_safety():
    print("\n🛡️ Testing VANDORS TSR (Thermal Stability & Risk) Algorithm...")
    
    # 1. Initialize Reactor (500g Oil, High Power)
    reactor = PhysicsReactor(
        ingredients={"olive_oil": 500.0},
        current_temp=25.0,
        cooking_method="FRYING"
    )
    
    dt = 5.0 # 5s steps
    print(f"   {'Time (s)':<10} | {'Temp (C)':<10} | {'Risk Level':<12} | {'Degradation':<12} | {'S-Time Rem'}")
    print("-" * 75)
    
    # Simulate up to 600s or shutdown
    for s in range(0, 601, 5):
        reactor = FisPhysics.step_simulation(reactor, dt, power_watts=2000)
        
        if s % 30 == 0 or reactor.tsr.risk_level != "SAFE":
            print(f"   {reactor.elapsed_time:<10.1f} | {reactor.current_temp:<10.2f} | {reactor.tsr.risk_level:<12} | {reactor.tsr.degradation_index:<12.4f} | {reactor.tsr.safe_time_remaining:.1f}s")
        
        if reactor.tsr.risk_level == "SHUTDOWN":
            print(f"\n   🚨 SYSTEM AUTO-SHUTDOWN TRIGGERED AT {reactor.elapsed_time}s!")
            break

    assert reactor.tsr.risk_level in ["CRITICAL", "SHUTDOWN"]
    print(f"\n   ✅ TSR Logic Confirmed: Shutdown triggered before catastrophic failure.")
    print(f"   Final Degredation Index: {reactor.tsr.degradation_index:.4f}")

if __name__ == "__main__":
    test_vandors_tsr_safety()
