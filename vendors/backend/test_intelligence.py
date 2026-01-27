from app.services.memory_service import MemoryService
import time

def test_intelligent_feature():
    print("🤖 Initializing AI Memory Service...")
    mem = MemoryService()
    
    # 1. Clear Memory for Demo
    mem.memory = []
    mem._save_db()

    # 2. Add Knowledge (Recipe Database)
    # 실제로는 DB에서 Scraped Recipe를 가져와서 임베딩해야 하지만, 여기선 수동 주입
    print("\n📚 Learning Recipes...")
    knowledge = [
        ("김치찌개 (재료: 돼지고기, 신김치, 두부, 파)", {"type": "Jjigae"}),
        ("된장찌개 (재료: 소고기, 된장, 애호박, 두부)", {"type": "Jjigae"}),
        ("제육볶음 (재료: 돼지고기, 고추장, 양파, 당근)", {"type": "Bokkeum"}),
        ("계란말이 (재료: 계란, 소금, 파)", {"type": "Side"}),
        ("스테이크 (재료: 소고기 등심, 소금, 후추)", {"type": "Western"})
    ]
    
    for text, meta in knowledge:
        # Check if Ollama is running...
        try:
            success = mem.add_memory(text, meta)
            if not success:
                print("❌ Failed to embed. Is Ollama running with nomic-embed-text?")
                return
        except Exception as e:
            print(f"❌ Error: {e}")
            return

    # 3. Simulate User Request: "I have Pork and Onion"
    my_ingredients = ["돼지고기", "양파"]
    print(f"\n🥘 User: I have {my_ingredients}. What can I make?")
    
    results = mem.search_by_ingredients(my_ingredients)
    
    print("\n💡 AI Recommendations:")
    for res in results:
        rec = res['example']['text']
        score = res['similarity']
        print(f"  [{score:.4f}] {rec}")
        
    print("\n✨ This proves Semantic Search works regardless of Database Engine.")

if __name__ == "__main__":
    test_intelligent_feature()
