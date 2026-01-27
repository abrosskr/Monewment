import time
import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def check_health():
    print("🏥 Checking Health...")
    for i in range(10):
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=2)
            if r.status_code == 200:
                print(f"✅ Health OK: {r.json()}")
                return True
        except Exception as e:
            print(f"  .. retrying ({e})")
        time.sleep(1)
    print("❌ Health Check Failed")
    return False

def run_prefill():
    print("📥 Triggering Prefill (3 recipes)...")
    try:
        r = requests.post(f"{BASE_URL}/training/cache/prefill?count=3", timeout=30)
        print(f"✅ Prefill Result: {r.json()}")
        return True
    except Exception as e:
        print(f"❌ Prefill Failed: {e}")
        return False

def start_worker():
    print("🧠 Starting Classification Worker...")
    try:
        r = requests.post(f"{BASE_URL}/training/cache/start-worker", timeout=5)
        print(f"✅ Worker Trigger: {r.json()}")
        return True
    except Exception as e:
        print(f"❌ Worker Start Failed: {e}")
        return False
        
def wait_for_classification():
    print("⏳ Waiting for classification...")
    for i in range(20):
        try:
            r = requests.get(f"{BASE_URL}/training/cache/status")
            data = r.json()
            print(f"  Status: {data}")
            if data.get('db_classified', 0) > 0 or data.get('memory_classified', 0) > 0:
                print("✅ Classification Detected!")
                return True
        except:
            pass
        time.sleep(2)
    print("⚠️ Timed out waiting for classification (might be slow/queueing)")
    return False

if __name__ == "__main__":
    if not check_health(): sys.exit(1)
    if not run_prefill(): sys.exit(1)
    if not start_worker(): sys.exit(1)
    wait_for_classification()
    
    print("\n🎉 SYSTEM FULLY OPERATIONAL")
