import os
import sys

def purge_evolution():
    EVOLVED_ONTOLOGY = os.path.join(os.getcwd(), "backend", "data", "ontology_evolved.json")
    CANDIDATES_FILE = os.path.join(os.getcwd(), "backend", "data", "ontology_candidates.json")
    
    print("\n🚨 [Emergency] Purging all Evolved Ontology Data...")
    
    purged = 0
    for file_path in [EVOLVED_ONTOLOGY, CANDIDATES_FILE]:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"   🗑️  Deleted: {os.path.basename(file_path)}")
            purged += 1
            
    if purged == 0:
        print("   ✅ No evolved data found. System is already in 'Core-Only' state.")
    else:
        print(f"\n✨ Purge Complete. System has been reset to its Core Ontology.")

if __name__ == "__main__":
    confirm = input("⚠️  Are you sure you want to WIPE all learned terminology? (y/n): ").lower()
    if confirm == 'y':
        purge_evolution()
    else:
        print("❌ Purge cancelled.")
