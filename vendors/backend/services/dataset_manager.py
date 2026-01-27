from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
import os
from datetime import datetime

class LabeledData(BaseModel):
    source_url: str
    physical_primitives: List[Dict[str, Any]]
    collected_at: str
    validation_score: Optional[float] = None

class DatasetManager:
    """
    [Data Reservoir]
    Stores the refined 'Physical Primitives' into a structured dataset
    Training ready for NVIDIA Isaac Sim or future ML models.
    """
    DATASET_PATH = os.path.join("data", "v_dataset.json")

    @classmethod
    def save_knowledge(cls, source: str, primitives: List[Any], score: float = None):
        """Append new knowledge to the master dataset file."""
        os.makedirs("data", exist_ok=True)
        
        entry = LabeledData(
            source_url=source,
            physical_primitives=[p.model_dump() for p in primitives],
            collected_at=datetime.utcnow().isoformat(),
            validation_score=score
        )
        
        # Simple JSON append for MVP
        current_data = []
        if os.path.exists(cls.DATASET_PATH):
            try:
                with open(cls.DATASET_PATH, "r", encoding="utf-8") as f:
                    current_data = json.load(f)
            except: pass
            
        current_data.append(entry.model_dump())
        
        with open(cls.DATASET_PATH, "w", encoding="utf-8") as f:
            json.dump(current_data, f, indent=2, ensure_ascii=False)

    @classmethod
    def get_stats(cls) -> Dict[str, int]:
        if not os.path.exists(cls.DATASET_PATH): return {"total_entries": 0}
        with open(cls.DATASET_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {"total_entries": len(data)}
