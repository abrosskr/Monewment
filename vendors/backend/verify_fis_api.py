from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

def test_fis_optimization():
    print("🧪 [FIS API Test] Starting...")

    # Case 1: Bulgogi Sauce (Salty + Sweet + Umami)
    # Vector: [Salt=10, Sweet=8, Umami=5, Spicy=0.2, Sour=0]
    # Expect: Soy_Base (Salt/Umami), Sugar_Syrup (Sweet) to be high
    target_vector = [10.0, 8.0, 5.0, 0.0, 0.0]
    
    print(f"\n🔹 Requesting Optimization for Target: {target_vector}")
    response = client.post("/api/fis/optimize", json={"vector": target_vector})
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API Call Successful!")
        print("🖨️  Ink Recipe Output:")
        print(json.dumps(data["recipe"], indent=2))
        print(f"📉 Error Rate: {data['error_rate']:.4f}")
        
        # Validation Logic
        if data["recipe"].get("Soy_Base", 0) > 1.0 and data["recipe"].get("Sugar_Syrup", 0) > 0.5:
             print("✅ Logic Verified: Soy Sauce and Sugar successfully selected.")
        else:
             print("⚠️ Logic Warning: Unexpected recipe result.")
    else:
        print(f"❌ API Failed: {response.status_code}")
        print(response.text)

    # Case 2: Spicy Cold Noodle (Spicy + Sour)
    # Vector: [Salt=5, Sweet=8, Umami=2, Spicy=25, Sour=10]
    target_spicy = [5.0, 8.0, 2.0, 25.0, 10.0]
    print(f"\n🔹 Requesting Optimization for Target (Spicy): {target_spicy}")
    response = client.post("/api/fis/optimize", json={"vector": target_spicy})
    
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data["recipe"], indent=2))
        if data["recipe"].get("Capsaicin", 0) > 0.3 and data["recipe"].get("Vinegar", 0) > 1.0:
            print("✅ Logic Verified: Capsaicin and Vinegar selected.")
    else:
        print(f"❌ API Failed: {response.status_code}")

if __name__ == "__main__":
    # Ensure dependencies
    try:
        test_fis_optimization()
    except ImportError:
        print("❌ httpx module missing. Use 'pip install httpx' to run TestClient.")
    except Exception as e:
        print(f"❌ Verification Error: {e}")
