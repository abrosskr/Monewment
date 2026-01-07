import asyncio
import sys
import os
import requests
from sqlalchemy import select

# Add root to sys.path
sys.path.insert(0, os.getcwd())

# Import actual DB components
try:
    from src.database import AsyncSessionLocal as async_session_factory
    from src.models import User
except ImportError:
    # If run from scripts/ dir, fix path
    sys.path.insert(0, os.path.dirname(os.getcwd()))
    from src.database import AsyncSessionLocal as async_session_factory
    from src.models import User

async def seed_test_user():
    print("🛠️ Seeding Test User...")
    async with async_session_factory() as db:
        # Check if exists
        result = await db.execute(select(User).where(User.api_key == 'test-key'))
        user = result.scalars().first()
        
        if not user:
            print("👤 Creating 'security_test' User with API Key 'test-key'...")
            new_user = User(
                email="security_test@monewment.ai",
                hashed_password="test_password_hash_mock",
                role="OWNER", 
                api_key="test-key"
            )
            db.add(new_user)
            await db.commit()
            print("✅ Test User Inserted.")
        else:
            print("ℹ️ Test User 'test-key' already exists.")

def test_header_verification():
    print("🛡️ Starting Security Verification: Asset Header Check")
    base_url = "http://127.0.0.1:8001"
    
    headers = {"X-API-Key": "test-key"}
    
    # 1. Test: Invalid File (Attack Simulation)
    print("\n[Test 1] Uploading Fake File (should fail)...")
    files = {'file': ('fake.blend', b'This is a txt file pretending to be blender')}
    try:
        res = requests.post(f"{base_url}/api/v1/vault/manager/upload/verify_header", files=files, headers=headers)
        if res.status_code == 400:
            print(f"✅ SUCCESS: Rejected invalid file. Status: {res.status_code}, Detail: {res.json()}")
        else:
            print(f"❌ FAILURE: Security Hole! Accepted invalid file (or other error). Status: {res.status_code}, Resp: {res.text}")
    except Exception as e:
        print(f"⚠️ Error: {e}")

    # 2. Test: Valid File (Normal Usage)
    print("\n[Test 2] Uploading Valid Header (should pass)...")
    # minimal blender header is b'BLENDER'
    files = {'file': ('valid.blend', b'BLENDER-v3.00')} 
    try:
        res = requests.post(f"{base_url}/api/v1/vault/manager/upload/verify_header", files=files, headers=headers)
        if res.status_code == 200:
            print(f"✅ SUCCESS: Accepted valid file. Status: {res.status_code}, Resp: {res.json()}")
        else:
            print(f"❌ FAILURE: False Positive or Auth Error! Status: {res.status_code}, Resp: {res.text}")
    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Seed DB first
    asyncio.run(seed_test_user())
    
    # Run Requests
    test_header_verification()
