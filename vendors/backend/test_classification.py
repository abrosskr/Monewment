# test_classifier.py
import sys
import os
import json

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.recipe_10k import Recipe10kScraper
from app.services.classifier import FoodClassifier

def run_test():
    print("🧠 Running Phase 3: The Brain (Full Pipeline Test)...")
    print("   [Scrape] -> [Normalize] -> [Classify]\n")
    
    # 1. Collect
    scraper = Recipe10kScraper()
    raw_recipes = scraper.run_batch(count=5) 
    
    # 2. Classify (Includes Normalization inside)
    classifier = FoodClassifier(db_session=None) # Mode without DB connection for quick test
    
    print("\n" + "="*80)
    print(f"{'MENU NAME':<30} | {'TYPE':<15} | {'BASE':<15} | {'PROTEIN (MODIFIER)':<20}")
    print("-" * 80)
    
    for recipe in raw_recipes:
        name = recipe['name']
        ingredients = recipe['ingredients']
        
        # 3. The Brain Working
        analysis = classifier.classify_recipe(name, ingredients)
        
        f_type = analysis['food_type'] or "Unknown"
        f_base = analysis['base'] or "?"
        f_protein = analysis['protein'] or "None"
        
        print(f"{name:<30} | {f_type:<15} | {f_base:<15} | {f_protein:<20}")
        # print(f"   Context: {ingredients[:3]}...") # Debug
        
    print("="*80)

if __name__ == "__main__":
    run_test()
