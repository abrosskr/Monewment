import json
import os
import sys

def manage_ontology():
    CORE_FILE = os.path.join(os.getcwd(), "backend", "data", "ontology_core.json")
    EVOLVED_FILE = os.path.join(os.getcwd(), "backend", "data", "ontology_evolved.json")
    CANDIDATES_FILE = os.path.join(os.getcwd(), "backend", "data", "ontology_candidates.json")

    if not os.path.exists(CANDIDATES_FILE):
        print("❌ No candidates found to review.")
        return

    with open(CANDIDATES_FILE, "r", encoding="utf-8") as f:
        candidates = json.load(f)

    # 1. Load Combined for view, but we only write to Evolved
    # Load Core
    if os.path.exists(CORE_FILE):
        with open(CORE_FILE, "r", encoding="utf-8") as f:
            core = json.load(f)
    else:
        core = {"origins": [], "states": [], "details": [], "main_categories": {}}

    # Load Evolved
    if os.path.exists(EVOLVED_FILE):
        with open(EVOLVED_FILE, "r", encoding="utf-8") as f:
            evolved = json.load(f)
    else:
        evolved = {"origins": [], "states": [], "details": [], "main_categories": {}}

    pending = {k: v for k, v in candidates.items() if v["status"] == "PENDING"}
    
    if not pending:
        print("✅ No pending candidates. Everything is clean!")
        return

    print(f"\n📢 [Ontology Guard] {len(pending)} terms need review.")
    print("="*40)

    for term, info in pending.items():
        print(f"\n🔍 Term: '{term}' (Found {info['count']} times)")
        print(f"   💡 Predicted Category: {info['predicted']}")
        
        choice = input("   ✅ Approve (a) / ❌ Reject (r) / ⏩ Skip (s): ").lower()
        
        if choice == 'a':
            cat = info['predicted']
            if cat == 'unknown':
                cat = input("      Enter category (origins/states/details): ")
            
            # Check if cat is valid
            if cat in evolved:
                # Add to evolved layer
                if term not in core.get(cat, []) and term not in evolved.get(cat, []):
                    evolved[cat].append(term)
                    candidates[term]["status"] = "APPROVED"
                    print(f"      ✨ Added to '{cat}' (Evolved Layer)!")
            else:
                 print(f"      ⚠️ Invalid category: {cat}. Skipping.")
                 
        elif choice == 'r':
            candidates[term]["status"] = "REJECTED"
            print("      🚫 Rejected.")
            
    # Save back (Only Evolved and Candidates)
    with open(EVOLVED_FILE, "w", encoding="utf-8") as f:
        json.dump(evolved, f, indent=2, ensure_ascii=False)
        
    with open(CANDIDATES_FILE, "w", encoding="utf-8") as f:
        json.dump(candidates, f, indent=2, ensure_ascii=False)

    print("\n✅ Session Complete.")

if __name__ == "__main__":
    manage_ontology()
