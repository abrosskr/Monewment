import logging
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class VersionedLayerKeeper:
    """
    [Grand Fortification: Data Integrity]
    Manages archival and versioning of the 3-Layer Archetype system.
    Strictly enforces 'Context-Core Separation'.
    """

    def __init__(self, db_session):
        self.db = db_session

    def archive_archetype(self, archetype_id: int, comment: str):
        """Creates a versioned snapshot of an archetype."""
        logger.info(f"📦 Versioning Archetype ID {archetype_id}: {comment}")
        # In a real system, this would write to a specialized 'archetype_versions' table
        # Here we simulate the integrity hash generation
        return self._generate_integrity_hash(archetype_id)

    def separation_filter(self, data: Dict, layer: str) -> Dict:
        """
        [Context-Core Separation Filter]
        Ensures 'Core' layer contains NO state-specific metadata (e.g., 'Frozen', 'Microwave').
        """
        if layer != "CORE":
            return data

        sanitized = data.copy()
        context_keywords = ["FROZEN", "MICROWAVE", "QUICK", "AIRFRYER", "PREHEATED"]
        
        # Strip context from notes
        if "optimization_notes" in sanitized:
            notes = sanitized["optimization_notes"]
            for kw in context_keywords:
                notes = notes.replace(kw, "[REDACTED_CONTEXT]")
            sanitized["optimization_notes"] = notes
            
        logger.info("🛡️ Context-Core Separation Filter applied to CORE layer.")
        return sanitized

    def _generate_integrity_hash(self, archetype_id: int) -> str:
        # Dummy hash generation for demonstration
        content = f"Archetype_{archetype_id}_{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()

    def check_integrity(self, core_data: Dict, unseen_data: Dict) -> bool:
        """
        [Cross-Layer Integrity Check]
        Verifies that Human-unseen layer doesn't fundamentally contradict Core truth.
        """
        core_ing = set(core_data.get("ingredients", []))
        unseen_ing = set(unseen_data.get("ingredients", []))
        
        # Violation if AI removes essential ingredients found in Core consensus
        if not core_ing.issubset(unseen_ing):
            missing = core_ing - unseen_ing
            logger.warning(f"🚨 INTEGRITY BREACH: Unseen layer removed core ingredients: {missing}")
            return False
            
        return True
