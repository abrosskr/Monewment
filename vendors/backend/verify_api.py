import requests
import json
import time

BASE_URL = "http://localhost:8010/v1"

print("⏳ Waiting for server to start...")
time.sleep(3)

# 1. Test Analysis API
print("\n🧪 Testing Analysis API (/analyze/text)...")
text_payload = {"text": "Boil the pork belly and kimchi for 30 minutes."}
try:
    resp = requests.post(f"{BASE_URL}/analyze/text", json=text_payload)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
except Exception as e:
    print(f"❌ Failed: {e}")

# 2. Test Recommendation API
print("\n🧪 Testing Recommendation API (/recommend/context)...")
inv_payload = {"inventory": ["pork", "kimchi", "onion"]}
try:
    resp = requests.post(f"{BASE_URL}/recommend/context", json=inv_payload)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Found {len(data)} matches.")
        if data:
            print(f"Top Match: {data[0]['recipe_name']} (Pivot: {data[0]['pivot_used']})")
    else:
        print(f"Error: {resp.text}")
except Exception as e:
    print(f"❌ Failed: {e}")
