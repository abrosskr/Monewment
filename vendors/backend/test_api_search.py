import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_search():
    print("🔍 Testing Ingredient Search API...")
    try:
        # Search for 'pork' (matches previously seeded 'Jjigae' or 'Katsu')
        r = requests.get(f"{BASE_URL}/training/search/ingredient?q=돼지고기")
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Search Success! Found match for '{data['query']}'")
            for res in data['results']:
                print(f"  - [{res['similarity']:.4f}] {res['example']['text']}")
            return True
        else:
            print(f"❌ Search Failed: {r.status_code} {r.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_search()
