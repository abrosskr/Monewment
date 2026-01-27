# test_llm_pipeline.py
import sys
import os
import time

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.llm_classifier import LLMClassifier
from app.scrapers.recipe_10k import Recipe10kScraper

def run_test():
    print("🧠 Running Phase 3-2: LLM Classifier (The Brain 2.0)...\n")
    
    # 1. Setup
    try:
        classifier = LLMClassifier()
        print("✅ Gemini Model Loaded.")
    except Exception as e:
        print(f"❌ Failed to load LLM: {e}")
        return

    # 2. Collect Real Data (Scraper)
    scraper = Recipe10kScraper()
    print("🕷️  Crowling 3 random recipes...")
    recipes = scraper.run_batch(count=3)
    
    print("\nProcessing with LLM...")
    print("="*80)
    
    for recipe in recipes:
        name = recipe['name']
        ingredients = recipe['ingredients']
        
        print(f"🍲 Analysing: {name}")
        print(f"   (Ingredients: {len(ingredients)} items)")
        
        start_time = time.time()
        result = classifier.classify(name, ingredients)
        duration = time.time() - start_time
        
        if result:
            print(f"   ⏱️  Time: {duration:.2f}s")
            print(f"   🏷️  Type    : {result.get('food_type_name')}")
            print(f"   🏗️  Base    : {result.get('base_material')}")
            print(f"   🍳 Method  : {result.get('default_method')}")
            print(f"   🍖 Protein : {result.get('protein_modifier')}")
            print(f"   🌶️  Primary : {result.get('primary_modifier')}")
            print(f"   🤔 Reason  : {result.get('reasoning')}")
        else:
            print("   ❌ Classification Failed.")
            
        print("-" * 80)

if __name__ == "__main__":
    run_test()
