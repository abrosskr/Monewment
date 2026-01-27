import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "knowledge_base.json")

# Unit Conversion Table (Standardized to mL)
# This is the "Stoichiometry Constant" set
UNIT_MAP = {
    "큰술": 15.0,
    "스푼": 15.0, # Assumed Table Spoon
    "숟가락": 15.0,
    "작은술": 5.0,
    "티스푼": 5.0,
    "컵": 200.0,
    "종이컵": 180.0,
    "T": 15.0,
    "t": 5.0,
    "ml": 1.0,
    "l": 1000.0,
    "약간": 0.5,   # Trace amount
    "적당량": 1.0, # Baseline amount
    "개": 0.0,    # 'Piece' is hard to volume-ize without item density, skipping (0.0)
    "봉": 0.0,
    "대": 0.0,
    "쪽": 0.0,
    "톨": 0.0
}

def standardize_quantity(quantity, unit):
    """
    Convert (Quantity, Unit) -> Milliliters (float)
    """
    if quantity is None:
        quantity = 1.0 # Default presence if no number

    # Normalize unit text
    if not unit:
        return 0.0 # No unit usually means "1 Piece" or arbitrary
        
    unit = unit.strip().lower()
    
    # 1. Direct Map
    if unit in UNIT_MAP:
        return quantity * UNIT_MAP[unit]
        
    # 2. Partial Match (e.g. "큰술(15ml)")
    for key, conversion in UNIT_MAP.items():
        if key in unit:
            return quantity * conversion
            
    return 0.0 # Unknown unit

def vectorize_database():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    print(f"Loading {DB_PATH}...")
    with open(DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    modified_count = 0
    
    for item in data:
        classification = item.get("classification", {})
        ratios = classification.get("flavor_ratios", [])
        
        if not ratios:
            continue
            
        # Create a new "flavor_vector" list
        # [{item: "Soy Sauce", ml: 45.0}, ...]
        vector_data = []
        has_valid_vector = False
        
        for ratio in ratios:
            item_name = ratio.get("item")
            qty = ratio.get("quantity")
            unit = ratio.get("unit")
            
            ml_value = standardize_quantity(qty, unit)
            
            # Enrich the existing ratio object (In-place update for easier debugging)
            ratio["standard_volume_ml"] = ml_value
            
            # Also build clean vector
            if ml_value > 0:
                vector_data.append({
                    "axis": item_name,
                    "magnitude": ml_value
                })
                has_valid_vector = True
        
        if has_valid_vector:
            classification["flavor_vector"] = vector_data
            modified_count += 1
            
    if modified_count > 0:
        print(f"Vectorized {modified_count} recipes.")
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        print("No parsable flavor ratios found.")

if __name__ == "__main__":
    vectorize_database()
