# test_normalization.py
import sys
import os
import json

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.recipe_10k import Recipe10kScraper
from app.services.normalizer import IngredientNormalizer

def run_test():
    print("🚀 Running Collector + Normalizer Pipeline Test...\n")
    
    # 1. Collect
    scraper = Recipe10kScraper()
    raw_recipes = scraper.run_batch(count=3) # Small batch
    
    # 2. Normalize
    normalizer = IngredientNormalizer()
    
    print("\nProcessing Results:")
    print("="*60)
    
    for recipe in raw_recipes:
        print(f"🍲 Menu: {recipe['name']}")
        print("-" * 30)
        
        for ing in recipe['ingredients']:
            raw_item = ing['item']
            raw_qty = ing['qty']
            
            # Combine for normalization context if needed, but usually Item Name is enough
            normalized_id = normalizer.normalize(raw_item)
            
            print(f" [Raw] {raw_item:<15} ({raw_qty})  ➡️  [Norm] {normalized_id}")
            
        print("="*60)

if __name__ == "__main__":
    run_test()
