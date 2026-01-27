import requests
import json
import time

BASE_URL = "http://localhost:8011"

def print_result(title, data):
    print(f"\n--- {title} ---")
    print(json.dumps(data, indent=2, ensure_ascii=False))

def audit():
    print("🚀 Starting Vendors Intelligence System Master Audit...")
    
    # Test 1: AI Extraction & Physics DB (Korean Context)
    print("\n[Test 1] Analyzing Korean Recipe...")
    payload1 = {"text": "Add 300g of pork and 100g of kimchi. Boil it."}
    res1 = requests.post(f"{BASE_URL}/v1/analyze/text", json=payload1).json()
    print_result("Korean Analysis Result", res1)

    # Test 2: Global DB Expansion (Italian Context)
    print("\n[Test 2] Analyzing Italian Recipe (Global Expansion check)...")
    payload2 = {"text": "Make a pasta with olive oil, garlic and tomato."}
    res2 = requests.post(f"{BASE_URL}/v1/analyze/text", json=payload2).json()
    print_result("Italian Analysis Result", res2)

    # Test 3: Recommendation with Context (Weather & Mood)
    print("\n[Test 3] Testing Recommendation Engine (RAINY + STRESSED)...")
    payload3 = {
        "inventory": ["신김치", "스팸", "두부"],
        "context": {"weather": "RAINY", "mood": "STRESSED"},
        "user_profile": {"authenticity_preference": "HIGH"}
    }
    # Note: We need some recipes in the 'mock' search service to return results.
    # Let's hope the search service has some defaults.
    res3 = requests.post(f"{BASE_URL}/v1/recommend/context", json=payload3).json()
    print_result("Contextual Recommendation Result", res3[:2]) # Top 2

    # Test 4: Variant Selection (Convenience Preference)
    print("\n[Test 4] Testing Variant Selection (CONVENIENCE)...")
    payload4 = {
        "inventory": ["신김치", "스팸"],
        "user_profile": {"convenience_preference": "HIGH"}
    }
    res4 = requests.post(f"{BASE_URL}/v1/recommend/context", json=payload4).json()
    print_result("Variant Recommendation Result", res4[:2]) # Top 2

if __name__ == "__main__":
    audit()
