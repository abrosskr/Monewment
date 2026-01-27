import sys
import os

# Add parent dir to sys.path to allow importing app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import Session
from backend.app.database import SessionLocal, engine
from backend.app.models import Base, StandardRecipe

# Ensure tables exist
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    # 1. Clear existing sample data (optional, for safety)
    # db.query(StandardRecipe).delete()
    
    samples = [
        {
            "name": "직화 무뼈 닭발",
            "material_category": "가금류",
            "material_detail": "닭고기(닭발)",
            "cooking_method": "볶음/구이",
            "taste_profile": ["매운맛", "불맛", "쫄깃한"],
            "cuisine_type": "한식",
            "standard_ingredients": [
                {"item": "무뼈닭발", "qty": "300g"},
                {"item": "고춧가루", "qty": "20g"},
                {"item": "청양고추", "qty": "10g"}
            ]
        },
        {
            "name": "옛날 통닭",
            "material_category": "가금류",
            "material_detail": "닭고기",
            "cooking_method": "튀김",
            "taste_profile": ["고소한", "바삭한", "담백한"],
            "cuisine_type": "한식",
            "standard_ingredients": [
                {"item": "생닭(통)", "qty": "600g"},
                {"item": "튀김가루", "qty": "100g"},
                {"item": "식용유", "qty": "500ml"} # Recalculated for absorption?
            ]
        },
        {
            "name": "숙성 삼겹살 구이",
            "material_category": "육류",
            "material_detail": "돼지고기(삼겹살)",
            "cooking_method": "구이",
            "taste_profile": ["고소한", "기름진", "감칠맛"],
            "cuisine_type": "한식",
            "standard_ingredients": [
                {"item": "통삼겹살", "qty": "200g"},
                {"item": "쌈장", "qty": "20g"},
                {"item": "상추", "qty": "50g"}
            ]
        },
        {
            "name": "해물 순두부 찌개",
            "material_category": "채소/곡물", # Main base is Tofu, but broth is seafood... let's say Composite? Or Tofu.
            # Ontology Rule: Main Protein takes precedence? Or naming?
            # Let's say "해산물" because '해물' is key. Or '채소'(두부). 
            # User ontology layer 1 has '채소/곡물'. 
            # Let's go with '복합(Composite)' or stick to '해산물' for value.
            "material_category": "해산물", 
            "material_detail": "조개/새우",
            "cooking_method": "탕(Stew)",
            "taste_profile": ["얼큰한", "시원한", "부드러운"],
            "cuisine_type": "한식",
            "standard_ingredients": [
                {"item": "순두부", "qty": "350g"},
                {"item": "바지락", "qty": "100g"},
                {"item": "계란", "qty": "1개"}
            ]
        }
    ]

    print(f"Adding {len(samples)} ontology samples...")
    for s in samples:
        # Check if exists
        exists = db.query(StandardRecipe).filter_by(name=s['name']).first()
        if not exists:
            recipe = StandardRecipe(**s)
            db.add(recipe)
            print(f" [+] Inserted: {s['name']} ({s['material_category']} > {s['material_detail']})")
        else:
            print(f" [.] Skipped (Exists): {s['name']}")
    
    db.commit()
    db.close()
    print("Seeding complete.")

if __name__ == "__main__":
    seed_data()
