import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.normalization_engine import NormalizationEngine
from app.engines.product_standard.parser import ProductDataParser
from app.engines.product_standard.codes import WeightUnit

def test_parsing():
    test_cases = [
        # Western Style (Qty Unit Name) + Multilingual Category
        ("1.5 cups Flour", 300.0, WeightUnit.ML, "밀가루"), 
        ("10 oz Beef", 283.5, WeightUnit.G, "소"),
        ("1/2 lb Butter", 226.795, WeightUnit.G, "버터"),
        ("3 cl de lait", 30.0, WeightUnit.ML, "우유"),
        ("2 Large Eggs", 120.0, WeightUnit.G, "계란"), # 2 * 60g(count)
        
        # Asian Style (Name Qty/Unit)
        ("合い挽き肉 300g", 300.0, WeightUnit.G, "돼지"), # Mix usually mapped to Pork
        ("玉ねぎ 1/2個", 100.0, WeightUnit.G, "양파"),    # 0.5 * 200 = 100
        ("大さじ 1 醤油", 15.0, WeightUnit.G, "간장"),
        
        # French/Mixed Style
        ("3 oignons jaunes", 180.0, WeightUnit.G, "양파"),
        ("1,5 kg de pommes", 1500.0, WeightUnit.G, "기타") # Not registered yet
    ]

    print("="*100)
    print(f"{'Input Text':<25} | {'Expected Cat':<12} | {'Actual Cat':<12} | {'Val (g/ml)':<12} | {'Status'}")
    print("-"*100)

    for text, expected_val, expected_unit, expected_cat in test_cases:
        pim = NormalizationEngine.parse_to_pim(text)
        actual_val = pim.mass_g
        actual_cat = pim.main_category
        
        val_ok = abs(actual_val - expected_val) < 0.1
        cat_ok = actual_cat == expected_cat
        
        status = "✅ PASS" if (val_ok and cat_ok) else "❌ FAIL"
        
        print(f"{text:<25} | {expected_cat:<12} | {actual_cat:<12} | {actual_val:<12.2f} | {status}")
        if status == "❌ FAIL":
             if not val_ok: print(f"   -> Val Mismatch: Expected {expected_val}, Got {actual_val}")
             if not cat_ok: print(f"   -> Cat Mismatch: Expected {expected_cat}, Got {actual_cat}")

    print("="*100)

if __name__ == "__main__":
    test_parsing()
