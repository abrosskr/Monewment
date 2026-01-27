import json
import re
import os

# Configuration
DB_PATH = "knowledge_base.json"

# Regex patterns for cleaning (Korean units & numbers)
# Matches: "1스푼", "2.5 큰술", "100g", "약간", "적당량" etc.
# Also handles format like "간장 1T"
UNIT_PATTERN = r'(\d+(?:\.\d+)?\s*(?:T|t|스푼|큰술|작은술|컵|g|ml|kg|l|개|마리|봉|봉지|모|단|줌|쪽|톨|방울|약간|적당량)|약간|적당량)'
PARENTHESIS_PATTERN = r'\(.*?\)'

def clean_ingredient_string(text):
    if not text:
        return ""
    
    # 1. Split by comma or newlines
    # The messy data has newlines: "간장\n\n 1스푼"
    parts = re.split(r'[,\n]+', text)
    
    cleaned_parts = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        # 2. Remove Parenthesis info (often brands or details)
        # e.g. "올리고당(또는 설탕)" -> "올리고당"
        part = re.sub(PARENTHESIS_PATTERN, '', part)
        
        # 3. Remove Units & Numbers
        part = re.sub(UNIT_PATTERN, '', part)
        
        # 4. Remove special chars and non-word chars except spaces
        # Keep Korean/English chars
        # part = re.sub(r'[^\w\s가-힣]', '', part) 
        
        # 5. Final strip
        part = part.strip()
        
        if part:
            cleaned_parts.append(part)
            
    # Deduplicate and join
    unique_parts = list(dict.fromkeys(cleaned_parts))
    return ", ".join(unique_parts)

def clean_database():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    print(f"Loading {DB_PATH}...")
    with open(DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    modified_count = 0
    
    for item in data:
        classification = item.get("classification", {})
        original_modifier = classification.get("primary_modifier", "")
        
        if original_modifier:
            cleaned = clean_ingredient_string(original_modifier)
            
            # Additional logic: remove whitespace duplication inside the string
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            
            if cleaned != original_modifier:
                print(f"Cleaning: [{original_modifier[:20]}...] -> [{cleaned}]")
                classification["primary_modifier"] = cleaned
                modified_count += 1
                
                # Also clean main_ingredient_source if it exists
                if classification.get("main_ingredient_source"):
                    raw_main = classification["main_ingredient_source"]
                    clean_main = clean_ingredient_string(raw_main)
                    if raw_main != clean_main:
                         classification["main_ingredient_source"] = clean_main

    if modified_count > 0:
        print(f"Saving {modified_count} modified records...")
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Done.")
    else:
        print("No changes needed.")

if __name__ == "__main__":
    clean_database()
