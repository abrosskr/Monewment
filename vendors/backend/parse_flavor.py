import json
import re
import os

# Configuration
# Configuration
DB_PATH = os.path.join(os.path.dirname(__file__), "knowledge_base.json")

# Advanced Regex for Korean Ingredient Parsing
# Group 1: Item Name
# Group 2: Quantity (Number)
# Group 3: Unit (Korean Units)
PARSE_REGEX = r'([가-힣a-zA-Z\s]+?)\s*(\d+(?:\.\d+)?(?:/\d+)?)\s*(스푼|큰술|작은술|컵|g|ml|kg|l|개|마리|봉|봉지|모|단|줌|쪽|톨|방울|약간|적당량|T|t)'

def parse_ingredient_string(text):
    """
    Parses "간장 1스푼, 설탕 2큰술" into structured list.
    """
    if not text:
        return []
        
    # Pre-clean: Remove parenthesis content
    text = re.sub(r'\(.*?\)', '', text)
    
    # Split by comma or newline
    raw_items = re.split(r'[,\n]+', text)
    
    structured_data = []
    
    for item in raw_items:
        item = item.strip()
        if not item: continue
        
        # Try to match Regex
        match = re.search(PARSE_REGEX, item)
        if match:
            name, quantity, unit = match.groups()
            
            # Normalize Quantity (Handle fractions if needed, simple float for now)
            try:
                # Basic fraction handling might be needed later, assuming float for now
                val = float(quantity)
            except:
                val = 1.0 # Default fallback
            
            structured_data.append({
                "item": name.strip(),
                "quantity": val,
                "unit": unit
            })
        else:
            # If no unit found, treat as entire item, boolean existence
            # Or "약간", "적당량" might be keywords
            structured_data.append({
                "item": item,
                "quantity": None, # Qualitative
                "unit": None
            })
            
    return structured_data

def enrich_database():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    print(f"Reading {DB_PATH}...")
    with open(DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    modified_count = 0
    
    for item in data:
        classification = item.get("classification", {})
        original_modifier = classification.get("primary_modifier", "")
        
        # If we have data and we haven't parsed it yet (or want to update)
        if original_modifier:
            parsed_data = parse_ingredient_string(original_modifier)
            
            # Store in NEW field "flavor_ratios"
            # This preserves original text for legacy, but adds high-dim data
            if parsed_data:
                classification["flavor_ratios"] = parsed_data
                item["classification"] = classification # Ensure update
                modified_count += 1
                
                print(f"Parsed '{original_modifier[:20]}...' -> {len(parsed_data)} items")

    if modified_count > 0:
        print(f"Enriched {modified_count} records with Flavor Ratios.")
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        print("No parsable records found.")

if __name__ == "__main__":
    enrich_database()
