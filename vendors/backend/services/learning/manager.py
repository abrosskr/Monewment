from typing import Dict, Any, List, Optional
from app.engines.v_academy.core import VAcademyEngine, PhysicalPrimitive
from app.services.learning.handlers.base import YouTubeHandler, Recipe10kHandler, BaseSourceHandler
from app.services.learning.compliance.service import ComplianceService
from app.services.dataset_manager import DatasetManager
from app.core.logging import logger

class LearningManager:
    """
    [V-Learning Manager]
    Orchestrates ingestion from multiple channels (YT, 10k Recipes, etc.)
    Ensures legality via ComplianceService.
    Protects against bot detection via Handler-level stealth.
    """

    def __init__(self, academy: VAcademyEngine):
        self.academy = academy
        self._handlers: Dict[str, BaseSourceHandler] = {
            "youtube": YouTubeHandler(),
            "10k_recipes": Recipe10kHandler()
        }

    async def ingest(self, source_type: str, source_id: str) -> Dict[str, Any]:
        """
        The Unified Command for Learning.
        Usage: ingest("youtube", "URL") or ingest("10k_recipes", "ID")
        """
        handler = self._handlers.get(source_type)
        if not handler:
            raise ValueError(f"Unknown source type: {source_type}")

        # 1. Check Compliance
        if not ComplianceService.check_rights(source_id):
            return {"error": "Source blocked due to compliance/copyright risk."}

        # 2. Fetch Raw (Handler deals with Bot detection/Stealth)
        raw_text = await handler.fetch_and_parse(source_id)
        
        # 3. Filter (Legal: Discard creative, keep physical facts)
        clean_facts = ComplianceService.filter_metadata(raw_text)

        # 4. Distill (Universal Physics)
        primitives = self.academy.process_transcript(clean_facts)

        # 5. Auto-Save to Reservoir
        if primitives:
            DatasetManager.save_knowledge(source=source_id, primitives=primitives)

        return {
            "source": source_id,
            "source_type": source_type,
            "absorbed_technique_count": len(primitives),
            "status": "Legally Compliant Physics Absorption Complete"
        }
