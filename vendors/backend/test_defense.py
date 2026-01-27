import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.v_compiler import VCompiler
from app.core.v_kernel import VKernel, SecurityException
from app.core.license_manager import LicenseManager

def test_defense_strategy():
    print("\n🛡️ Testing Defense Strategy: Encryption & Access Control")
    print("-" * 80)

    # 1. Test Compiler & Kernel (The Black Box)
    secret_recipe = {
        "name": "Gordon's Beef Wellington",
        "steps": [{"action": "sear", "temp": 200, "duration": 120}],
        "secret_additive": "Truffle Oil 0.5g"
    }
    
    print("   [Compiler] Encrypting Recipe...")
    vdr_blob = VCompiler.compile(secret_recipe)
    print(f"   -> Blob Size: {len(vdr_blob)} bytes (First 16 bytes: {vdr_blob[:16].hex()}...)")
    
    # Verify it's not plain JSON
    assert b"Gordon" not in vdr_blob
    print("   ✅ SUCCESS: Data is obfuscated.")
    
    print("   [Kernel] Decrypting Recipe in Memory...")
    loaded_data = VKernel.load(vdr_blob)
    assert loaded_data["name"] == "Gordon's Beef Wellington"
    print("   ✅ SUCCESS: Integrity verified & Decrypted correctly.")
    
    # Test Tampering
    print("   [Security] Testing Tamper Resistance...")
    tampered_blob = vdr_blob[:-1] + b'\x00' # Change last byte
    try:
        VKernel.load(tampered_blob)
        print("   ❌ FAILURE: Tampered data was accepted!")
    except SecurityException:
        print("   ✅ SUCCESS: Tampered data rejected (HMAC Check).")

    # 2. Test License Manager
    print("\n   [License] Testing Tiered Access...")
    
    user_t1 = LicenseManager("TIER_1")
    user_t3 = LicenseManager("TIER_3")
    
    print(f"   Tier 1 Access to V_BRIDGE: {user_t1.can_access('V_BRIDGE')}")
    print(f"   Tier 3 Access to V_BRIDGE: {user_t3.can_access('V_BRIDGE')}")
    
    assert user_t1.can_access("V_BRIDGE") == False
    assert user_t3.can_access("V_BRIDGE") == True
    
    print(f"   Tier 1 Precision: {user_t1.get_parameter_precision()}s")
    print(f"   Tier 3 Precision: {user_t3.get_parameter_precision()}s")
    
    assert user_t3.get_parameter_precision() < user_t1.get_parameter_precision()
    print("   ✅ SUCCESS: Tiered restrictions are active.")

if __name__ == "__main__":
    test_defense_strategy()
