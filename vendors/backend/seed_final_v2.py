import os
import sys
import json

# Ensure backend path is in sys.path
sys.path.append(os.getcwd())

from app.database import engine, Base, SessionLocal
from app.models.recipe import ScrapedRecipe

print('🧹 Cleaning database...')
db_file = 'vendors_local_v2.db'
if os.path.exists(db_file):
    os.remove(db_file)

print('🔨 Creating tables...')
Base.metadata.create_all(bind=engine)

print('🌱 Seeding 20 recipes...')
db = SessionLocal()

# Mock classification result
jjigae_meta = {
    "food_type_name": "Jjigae",
    "base_material": "Broth",
    "default_method": "Boil",
    "protein_modifier": "Pork",
    "primary_modifier": "Kimchi",
    "reasoning": "Standard Kimchi Jjigae with pork."
}

recipes_data = [
    ('김치찌개', [{'item': 'pork', 'qty': '200g'}, {'item': 'kimchi', 'qty': '1/4'}], jjigae_meta),
    ('된장찌개', [{'item': 'beef', 'qty': '100g'}, {'item': 'tofu', 'qty': '1/2'}], None),
    ('제육볶음', [{'item': 'pork', 'qty': '300g'}, {'item': 'onion', 'qty': '1'}], None),
    ('계란말이', [{'item': 'egg', 'qty': '3'}, {'item': 'green onion', 'qty': '1'}], None),
    ('스테이크', [{'item': 'beef ribeye', 'qty': '300g'}, {'item': 'salt', 'qty': '1'}], None),
]

# Fill up to 20
for i in range(6, 21):
    recipes_data.append((f"레시피 {i}", [{"item": "ingredient", "qty": "some"}], None))

for i, (name, ing, meta) in enumerate(recipes_data):
    new_r = ScrapedRecipe(
        url=f'http://test.com/{i}',
        name=name,
        ingredients=ing,
        classification=meta,
        classified=True if meta else False,
        used=False
    )
    db.add(new_r)

db.commit()
db.close()
print(f'✅ Seeded {len(recipes_data)} recipes (1 pre-classified).')
