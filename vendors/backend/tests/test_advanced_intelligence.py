import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.normalization_engine import NormalizationEngine

def test_intelligence():
    test_cases = [
        # 1. High Confidence & Matching
        ("양파 1개", 1, "양파", 1.0),
        ("Butter 100g", 1, "버터", 0.9),
        
        # 2. Pattern Splitting
        ("Salt and Pepper 5g", 2, "소금", 0.9), # Now matched!
        ("Sugar & Cinnamon", 2, "설탕", 0.9),
        ("Sucre et Farine", 2, "설탕", 0.9), 
        ("Wasabi + Shoyu", 2, "기타", 0.4), # Wasabi not in core yet
        
        # 3. Noisy residues
        ("Unknown magical leaves 10g", 1, "기타", 0.4)
    ]

    print("="*100)
    print(f"{'Input Text':<30} | {'Count':<6} | {'First Cat':<12} | {'Conf':<6} | {'Status'}")
    print("-"*100)

    for text, exp_count, exp_cat, min_conf in test_cases:
        pims = NormalizationEngine.parse_multilingual_group(text)
        
        count_ok = len(pims) == exp_count
        cat_ok = pims[0].main_category == exp_cat
        conf_ok = pims[0].confidence >= min_conf - 0.1
        
        status = "✅ PASS" if (count_ok and cat_ok and conf_ok) else "❌ FAIL"
        
        print(f"{text:<30} | {len(pims):<6} | {pims[0].main_category:<12} | {pims[0].confidence:<6.2f} | {status}")
        if status == "❌ FAIL":
            print(f"   -> Details: Exp Count {exp_count}, Actual {len(pims)} | First Cat: {pims[0].main_category}")

    print("="*100)

if __name__ == "__main__":
    test_intelligence()
