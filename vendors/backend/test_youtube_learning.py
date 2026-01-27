import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.engines.v_academy.core import VAcademyEngine
from app.services.learning_service import LearningService

async def test_youtube_to_physics_learning():
    print("\n📹 Testing Global V-Learning: Multi-Language to Universal Physics...")
    print("-" * 80)
    
    academy = VAcademyEngine()
    learner = LearningService(academy)
    
    # 1. User provides a YouTube Link (could be Korean, English, etc.)
    youtube_url = "https://youtube.com/watch?v=global_chef_secrets"
    
    # 2. Extract knowledge
    print(f"   Action: Absorbing knowledge from {youtube_url}...")
    knowledge = await learner.learn_from_youtube(youtube_url, language="ko")
    
    # 3. Print extracted primitives
    print(f"\n   Detected Physical Primitives (Atomic Knowledge):")
    for p in knowledge["detected_primitives"]:
        print(f"      - ID: {p['id']}")
        print(f"      - Categorized: {p['category']}")
        print(f"      - Universal Name: {p['name']}")
        print(f"      - Logic: {p['logic_pattern']}")
        print(f"      - Context Tags: {p['context_tags']}")
        print("-" * 40)
        
    # Validation
    assert len(knowledge["detected_primitives"]) >= 2
    names = [p["name"] for p in knowledge["detected_primitives"]]
    assert "Incremental Hydration" in names
    assert "Residual Heat Resting" in names
    
    print(f"\n   ✅ SUCCESS: {len(knowledge['detected_primitives'])} universal primitives absorbed.")
    print(f"   🌐 Global Library Size: {knowledge['global_library_size']} techniques available for any recipe.")

if __name__ == "__main__":
    asyncio.run(test_youtube_to_physics_learning())
