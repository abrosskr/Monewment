import requests
import json
import time

BASE_URL = "http://localhost:8010/v1"

print("⏳ Waiting for server to reload...")
time.sleep(3)

# Test Advanced Context
print("\n🧪 Testing Advanced Context (Weather=RAINY, Auth=HIGH)...")

payload = {
    # Actual data has "신김치", "스팸", etc.
    "inventory": ["신김치", "스팸", "밥", "참기름"], 
    "context": {
        "weather": "RAINY",
        "mood": "STRESSED" # STRESSED triggers spicy/sweet boost if implemented
    },
    "user_profile": {
        "authenticity_preference": "LOW", # Should trigger K-Style
        "convenience_preference": "HIGH"
    }
}

try:
    resp = requests.post(f"{BASE_URL}/recommend/context", json=payload)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Found {len(data)} matches.")
        for item in data[:3]:
            print(f"🥘 [ {item['variant_name']} ]")
            print(f"   - Score: {item['completeness']} (Boost: x{item['score_boost']})")
            print(f"   - Base: {item['recipe_name']}")
    else:
        print(f"Error: {resp.text}")
except Exception as e:
    print(f"❌ Failed: {e}")
