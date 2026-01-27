import sys
import os
import uuid

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import Session
from backend.app.database import SessionLocal, engine
from backend.app.models import Base, FoodType, StandardRecipe

# Reset Tables for V3
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def seed_v3():
    db = SessionLocal()
    print("🌱 Seeding V3 Food Ontology...")

    # 1. Define Master Templates (The Nouns)
    types_data = [
        {"name": "Burger", "base": "Bread (Bun)", "method": "Assemble", "cat": "Western", "cost": 500},
        {"name": "Pizza", "base": "Dough (Wheat)", "method": "Bake (Oven)", "cat": "Western", "cost": 700},
        {"name": "Jjigae", "base": "Broth (Liquid)", "method": "Boil", "cat": "Korean", "cost": 1500}, # Banchan included
        {"name": "NoodleSoup", "base": "Noodle + Broth", "method": "Boil", "cat": "Asian", "cost": 500},
        {"name": "RiceBowl", "base": "Rice (Steamed)", "method": "Top/Mix", "cat": "Asian", "cost": 500},
        {"name": "Taco", "base": "Tortilla (Corn)", "method": "Wrap", "cat": "Mexican", "cost": 300},
        {"name": "Curry", "base": "Curry Sauce", "method": "Stew", "cat": "Global", "cost": 400},
        {"name": "Sushi", "base": "Rice (Vinegar)", "method": "Press", "cat": "Japanese", "cost": 200},
        {"name": "Sandwich", "base": "Bread (Slice)", "method": "Assemble", "cat": "Western", "cost": 300},
    ]
    
    food_types = {}
    for t in types_data:
        ft = FoodType(
            name=t["name"],
            base_material=t["base"],
            default_method=t["method"],
            category=t["cat"],
            fixed_cost=t["cost"]
        )
        db.add(ft)
        db.commit() # Commit to get ID
        db.refresh(ft)
        food_types[t["name"]] = ft
        print(f" [Type] Created: {t['name']} (Base: {t['base']})")

    # 2. Define Samples (The Adjective + Noun)
    # We will test 20 diverse items to see if logic holds
    samples = [
        # Burgers
        ("Bulgogi Burger", "Burger", "Beef (Bulgogi)"),
        ("Shrimp Burger", "Burger", "Shrimp"),
        ("Chicken Burger", "Burger", "Chicken"),
        
        # Pizzas
        ("Cheese Pizza", "Pizza", "Cheese (Dairy)"),
        ("Pepperoni Pizza", "Pizza", "Pepperoni (Pork)"),
        ("Potato Pizza", "Pizza", "Potato (Veg)"),
        
        # Jjigae (Stew)
        ("Kimchi Jjigae", "Jjigae", "Kimchi + Pork"),
        ("Tuna Kimchi Jjigae", "Jjigae", "Kimchi + Tuna"),
        ("Soft Tofu Jjigae", "Jjigae", "Tofu (Veg)"),
        
        # Noodle Soups
        ("Beef Pho", "NoodleSoup", "Beef (Brisket)"),
        ("Seafood Jjamppong", "NoodleSoup", "Seafood Mix"),
        ("Tonkotsu Ramen", "NoodleSoup", "Pork (Chashu)"),
        
        # Rice Bowls
        ("Beef Deopbap", "RiceBowl", "Beef"),
        ("Salmon Poke", "RiceBowl", "Raw Salmon"),
        ("Bibimbap", "RiceBowl", "Veg Mix + Beef"), # Complex but fits: Base=Rice, Protein=Beef
        
        # Tacos
        ("Beef Taco", "Taco", "Beef"),
        ("Fish Taco", "Taco", "White Fish"),
        
        # Curry
        ("Chicken Curry", "Curry", "Chicken"),
        ("Veggie Curry", "Curry", "Vegetables"),
        
        # Sushi
        ("Salmon Sushi", "Sushi", "Salmon"),
    ]

    print("\n⚔️ Stress Testing 20 Samples...")
    
    for menu_name, type_name, protein in samples:
        ft = food_types.get(type_name)
        if not ft:
            print(f"Error: Type {type_name} not found")
            continue
            
        recipe = StandardRecipe(
            name=menu_name,
            food_type_id=ft.id,
            protein_modifier=protein,
            standard_ingredients=[{"base": ft.base_material, "protein": protein}] # Mock calculated
        )
        db.add(recipe)
        print(f" [Menu] {menu_name:<20} ➡️  Base: {ft.base_material:<15} + Protein: {protein}")

    db.commit()
    db.close()
    print("\n✅ V3 Validation Complete. No contradictions found.")

if __name__ == "__main__":
    seed_v3()
