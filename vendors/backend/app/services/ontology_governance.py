import json
import os
import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel

class OntologyHypothesis(BaseModel):
    residue: str
    proposed_category: str
    source_url: str
    confidence: float
    detected_at: str

class OntologyGovernanceService:
    """
    [The Supreme Court of Data]
    Enforces Constitution Section 4: Residues are hypotheses, not truth.
    Expert-led ratification is mandatory for Core Ontology (Law) evolution.
    """
    HYPOTHESIS_FILE = "backend/data/residue_hypotheses.json"
    LAW_FILE = "backend/data/ontology_core.json"
    HISTORY_DIR = "backend/data/ontology_history"

    @classmethod
    def propose_hypothesis(cls, residue: str, context_url: str, confidence_score: float) -> str:
        """New/Unknown data is stored as a hypothesis (Untrusted)"""
        hypotheses = []
        if os.path.exists(cls.HYPOTHESIS_FILE):
            with open(cls.HYPOTHESIS_FILE, "r", encoding="utf-8") as f:
                hypotheses = json.load(f)
        
        # Avoid duplicate hypotheses for same residue
        if any(h['residue'] == residue for h in hypotheses):
            return "EXISTS"

        new_h = OntologyHypothesis(
            residue=residue,
            proposed_category="PENDING_ANALYSIS",
            source_url=context_url,
            confidence=confidence_score,
            detected_at=datetime.datetime.now().isoformat()
        )
        
        hypotheses.append(new_h.model_dump())
        
        with open(cls.HYPOTHESIS_FILE, "w", encoding="utf-8") as f:
            json.dump(hypotheses, f, indent=2)
        
        return "PROPOSED"

    @classmethod
    def ratify_law(cls, residue: str, approved_category: str, expert_note: str):
        """Constitution Section 4: Human/Expert Approval turns Hybrid/Hypothesis into Law"""
        # 1. Archive current Law (Versioning)
        os.makedirs(cls.HISTORY_DIR, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with open(cls.LAW_FILE, "r", encoding="utf-8") as f:
            current_law = json.load(f)
            
        history_file = os.path.join(cls.HISTORY_DIR, f"ontology_v_{timestamp}.json")
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(current_law, f, indent=2)

        # 2. Update Law
        if approved_category not in current_law["main_categories"]:
            current_law["main_categories"][approved_category] = {"synonyms": [residue], "sub": []}
        else:
            current_law["main_categories"][approved_category]["synonyms"].append(residue)
        
        # 3. Commit Law (Immutable Truth)
        with open(cls.LAW_FILE, "w", encoding="utf-8") as f:
            json.dump(current_law, f, indent=2)
            
        # 4. Cleanup Hypothesis
        if os.path.exists(cls.HYPOTHESIS_FILE):
            with open(cls.HYPOTHESIS_FILE, "r", encoding="utf-8") as f:
                hypotheses = json.load(f)
            
            hypotheses = [h for h in hypotheses if h['residue'] != residue]
            
            with open(cls.HYPOTHESIS_FILE, "w", encoding="utf-8") as f:
                json.dump(hypotheses, f, indent=2)
        
        return f"RATIFIED: {residue} -> {approved_category}"
