import os
import sys

# Ensure backend path is in sys.path
sys.path.append(os.getcwd())

from app.database import engine, Base, SessionLocal
from app.models.recipe import ScrapedRecipe
from app.services.memory_service import MemoryService

print('🧹 Cleaning database...')
db_file = 'vendors_local_v2.db'
if os.path.exists(db_file):
    try:
        os.remove(db_file)
        print(f'  Removed {db_file}')
    except Exception as e:
        print(f'  Failed to remove {db_file}: {e}')

print('🔨 Creating tables...')
Base.metadata.create_all(bind=engine)

print('🌱 Seeding recipes...')
db = SessionLocal()
recipes = [
    {'url': 'http://test.com/1', 'name': '김치찌개', 'ingredients': [{'item': 'pork', 'qty': '200g'}, {'item': 'kimchi', 'qty': '1/4'}]},
    {'url': 'http://test.com/2', 'name': '된장찌개', 'ingredients': [{'item': 'beef', 'qty': '100g'}, {'item': 'tofu', 'qty': '1/2'}]},
    {'url': 'http://test.com/3', 'name': '제육볶음', 'ingredients': [{'item': 'pork', 'qty': '300g'}, {'item': 'onion', 'qty': '1'}]},
    {'url': 'http://test.com/4', 'name': '계란말이', 'ingredients': [{'item': 'egg', 'qty': '3'}, {'item': 'green onion', 'qty': '1'}]},
    {'url': 'http://test.com/5', 'name': '스테이크', 'ingredients': [{'item': 'beef ribeye', 'qty': '300g'}, {'item': 'salt', 'qty': '1'}]},
]

for r in recipes:
    new_r = ScrapedRecipe(
        url=r['url'],
        name=r['name'],
        ingredients=r['ingredients'],
        classified=False,
        used=False
    )
    db.add(new_r)
db.commit()
db.close()
print(f'✅ Seeded {len(recipes)} recipes.')
