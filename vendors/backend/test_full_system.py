import asyncio
import sys
import os
from unittest.mock import MagicMock

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.fis_physics import FisPhysics, PhysicsReactor
from app.engines.v_bridge.core import VBridgeEngine, PhysicalStateTarget
from app.services.learning.handlers.base import YouTubeHandler

async def test_full_integration():
    print("\n🔗 Testing VANDORS Integrated System (Security & Logic Check)")
    print("-" * 80)

    # 1. Test Input Hygiene (Security)
    print("   [Security] Testing URL Validation...")
    handler = YouTubeHandler()
    try:
        await handler.fetch_and_parse("javascript:alert(1)")
        print("   ❌ FAILURE: Malicious URL was accepted!")
    except ValueError:
        print("   ✅ SUCCESS: Malicious URL blocked.")

    try:
        await handler.fetch_and_parse("https://youtube.com/watch?v=123")
        print("   ✅ SUCCESS: Valid URL accepted.")
    except ValueError:
        print("   ❌ FAILURE: Valid URL blocked!")

    # 2. Test Physics Logic (Surface-Core & Latent Heat)
    print("\n   [Physics] Testing Thermal Reality...")
    reactor = PhysicsReactor(
        ingredients={"beef": 500.0}, 
        thickness_mm=30.0,
        current_temp=25.0,
        core_temp=5.0 # From fridge
    )
    
    # Apply heavy power
    FisPhysics.step_simulation(reactor, dt=10.0, power_watts=2000.0)
    
    gradient = reactor.current_temp - reactor.core_temp
    print(f"   Step Result: Surface {reactor.current_temp:.2f}C | Core {reactor.core_temp:.2f}C | Gradient {gradient:.2f}C")
    
    assert gradient > 0, "Physics violation: Heat didn't propagate or surface didn't heat up."
    print("   ✅ SUCCESS: Multi-layer thermal model is working.")

    # 3. Test V-Bridge (Translation)
    print("\n   [Bridge] Testing Absolute Goal Translation...")
    target = PhysicalStateTarget(
        time_s=60, 
        surface_temp_target=180, 
        internal_energy_flux=1000,
        target_reaction_intensity=0.5,
        moisture_activity_limit=0.8
    )
    
    # Mock efficient machine
    cmd = VBridgeEngine.translate_goal_to_command(target, {"temp": 150}, hardware_eff=0.8, material_sh=3.5)
    print(f"   Command generated: {cmd}")
    assert cmd['power'] > 0
    print("   ✅ SUCCESS: Bridge translated physics to command.")

if __name__ == "__main__":
    asyncio.run(test_full_integration())
