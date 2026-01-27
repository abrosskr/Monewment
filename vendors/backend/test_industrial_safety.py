import sys
import os

# Add relevant paths
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.safety_engine.core.tsr_engine import IndustrialSafetyEngine, TSRState, SafetyContext

def test_industrial_server_room_monitoring():
    print("\n🏢 Scenario: Data Center Rack Cooling Failure...")
    
    # 1. Industrial context (Lower threshold for electronics)
    context = SafetyContext(
        hazard_activation_energy=110000, # Higher Ea for electrical degradation
        critical_threshold_temp=85.0,    # 85C is critical for CPUs
        warning_buffer_seconds=120,      # 2 minutes warning
        critical_buffer_seconds=45       # 45 seconds to hard-shutdown
    )
    
    state = TSRState()
    
    # Simulate rapid temp rise (Cooling fan failure)
    print(f"   {'Time (s)':<10} | {'Temp (C)':<10} | {'Risk Level':<12} | {'Safe Time Rem'}")
    print("-" * 60)
    
    ambient = 25.0
    for s in range(0, 301, 10):
        # Temp rises 2 degrees every 10 seconds
        current_temp = ambient + (s * 0.25)
        state = IndustrialSafetyEngine.update_state(state, current_temp, 10.0, context)
        
        print(f"   {s:<10} | {current_temp:<10.2f} | {state.risk_level:<12} | {state.safe_time_remaining:.1f}s")
        
        if state.risk_level == "SHUTDOWN":
            print(f"\n   🚨 [INDUSTRIAL SHUTDOWN] Hard power-off triggered at {current_temp}C")
            break

    assert state.risk_level in ["SHUTDOWN", "CRITICAL"]
    print("\n   ✅ Industrial Isolation Test Passed.")

if __name__ == "__main__":
    test_industrial_server_room_monitoring()
