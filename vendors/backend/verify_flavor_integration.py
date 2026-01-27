from app.services.memory_service import MemoryService
import json

def test_integration():
    print("🧪 Testing Flavor Integration...")
    mem = MemoryService()
    
    # 1. Add New Recipe with Flavor
    test_text = "Test Blueberry Jam (Blueberry 100g, Sugar 50g)"
    test_class = {
        "food_type_name": "Jam",
        "primary_modifier": "초콜릿 100g, 우유 200ml" # Korean parsing test
    }
    
    print(f"Adding: {test_text}")
    mem.add_memory(test_text, test_class)
    
    # 2. Check DB for vector
    last_item = mem.memory[-1]
    if "flavor_vector" in last_item["classification"]:
        print("✅ Flavor Vector Generated!")
        print(json.dumps(last_item["classification"]["flavor_vector"], indent=2, ensure_ascii=False))
    else:
        print("❌ Flavor Vector Missing!")
        return

    # 3. Test Search
    print("\n🔍 Testing Search by Taste...")
    target_vector = [
        {"axis": "초콜릿", "magnitude": 100.0},
        {"axis": "우유", "magnitude": 200.0}
    ]
    results = mem.search_by_taste_profile(target_vector, k=1)
    
    if results:
        print(f"Found: {results[0].get('food_type_name')}")
        if results[0].get('food_type_name') == "Jam":
            print("✅ Search Successful!")
        else:
            print("⚠️ Search result mismatch.")
    else:
        print("❌ No results found.")

if __name__ == "__main__":
    test_integration()
