from app.services.search_service import SearchService
import json

def test_semantic_search():
    print("🔍 Testing Semantic Search Engine (Vector-Enabled)...")
    
    # User provides a non-standard name "삼겹살" (Samgyeopsal)
    # The cache should map it to "pork_belly" or "pork".
    # And it should find recipes that mention "Pork" or "돼지고기".
    user_inventory = ["Pig meat", "kimchi"]
    
    print(f"Inventory: {user_inventory}")
    results = SearchService.reverse_search(user_inventory)
    
    if results:
        print(f"✅ Found {len(results)} matches!")
        # Print top 3
        for r in results[:3]:
            print(f"- {r['recipe_name']} (Completeness: {r['completeness']}%, Pivot: {r['pivot_used']})")
    else:
        print("❌ No matches found. Semantic mapping might have failed or repository empty.")

if __name__ == "__main__":
    test_semantic_search()
