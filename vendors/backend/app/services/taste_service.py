import json
import os
from typing import Dict, Optional
from datetime import datetime
from app.database import SessionLocal
from app.models import HumanTasteAsset

class TasteAssetService:
    """
    [Layer C: Human Evaluation Hub]
    Ingests blind test results and links them to Layer B (Physics).
    """
    DATA_PATH = "backend/data/assets/layer_c_taste"

    @classmethod
    def ingest_evaluation(cls, session_id: str, scores: Dict, cluster: str = "GENERIC") -> bool:
        db = SessionLocal()
        try:
            # 1. Store in DB for fast lookup
            eval_asset = HumanTasteAsset(
                phys_asset_id=session_id, # Can be string UUID or ID mapping
                juiciness=scores.get('juiciness', 0.0),
                crispness=scores.get('crispness', 0.0),
                doneness_consistency=scores.get('doneness', 0.0),
                preference_category=cluster
            )
            db.add(eval_asset)
            db.commit()

            # 2. Store JSON backup in Asset Path
            os.makedirs(cls.DATA_PATH, exist_ok=True)
            file_path = os.path.join(cls.DATA_PATH, f"{session_id}_human.json")
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({
                    "session_id": session_id,
                    "scores": scores,
                    "cluster": cluster,
                    "timestamp": datetime.utcnow().isoformat()
                }, f, indent=2)

            return True
        except Exception as e:
            print(f"❌ Taste Asset Ingestion Error: {e}")
            db.rollback()
            return False
        finally:
            db.close()
