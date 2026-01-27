import json
import os
import glob
from collections import Counter
from typing import List, Dict

class OntologyLearner:
    """
    [The Evolution Engine]
    Analyzes 'residue' and manages Ontology Staging.
    """
    ONTOLOGY_FILE = os.path.join(os.getcwd(), "backend", "data", "ontology_v1.json")
    CANDIDATES_FILE = os.path.join(os.getcwd(), "backend", "data", "ontology_candidates.json")
    FIS_REPO = os.path.join(os.getcwd(), "data", "fis_repo")

    def learn_new_patterns(self):
        print("\n🧠 [Evolution] Scanning for new patterns (Guarded Mode)...")
        residues = self._harvest_residues()
        
        if not residues:
            print("   ⏩ No new residues discovered.")
            return

        # 1. Update Candidate Pool
        candidates = self._load_json(self.CANDIDATES_FILE, {})
        new_discoveries = 0
        
        counter = Counter(residues)
        for term, freq in counter.items():
            if term not in candidates:
                candidates[term] = {
                    "count": 0,
                    "predicted": self._simulate_ai_categorization(term),
                    "status": "PENDING"
                }
                new_discoveries += 1
            candidates[term]["count"] += freq
            
        # 2. Save Candidates
        self._save_json(self.CANDIDATES_FILE, candidates)
        print(f"   ✅ Done: Recorded {new_discoveries} new terms in Staging Area.")
        print(f"   ℹ️ Total candidates pending review: {len(candidates)}")

    def _harvest_residues(self) -> List[str]:
        # Implementation: Scan FIS files or a dedicated residue log
        # For prototype, we simulate finding terms from recipes
        return ["수경재배", "노지", "유정란", "무항생제", "포항", "오가닉", "무농약재배"]

    def _simulate_ai_categorization(self, term: str) -> str:
        if term in ["수경재배", "노지", "유정란", "무항생제", "오가닉", "무농약재배"]:
            return "details"
        return "unknown"

    def _load_json(self, path: str, default: Any) -> Any:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return default

    def _save_json(self, path: str, data: Any):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    learner = OntologyLearner()
    learner.learn_new_patterns()
