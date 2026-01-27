from typing import Dict, List, Any, Optional
from pydantic import BaseModel

class ExtractionResult(BaseModel):
    entities: List[str]
    parameters: Dict[str, float]
    source_confidence: float

class VExtractionEngine:
    """
    [V-Extraction]
    Formal interface for unstructured->physical conversion.
    While implementations may use LLMs (Ollama), this core handles 
    validation and schema mapping.
    """

    @classmethod
    def map_to_physics_schema(cls, raw_data: Dict[str, Any]) -> ExtractionResult:
        """Ensures extracted data conforms to V-Engine standards."""
        # Baseline mapping logic
        entities = raw_data.get("ingredients", raw_data.get("materials", []))
        parameters = {
            "duration": raw_data.get("time_s", 60.0),
            "intensity": raw_data.get("heat_level", 1.0),
            "target_value": raw_data.get("goal_temp", 100.0)
        }
        return ExtractionResult(
            entities=entities,
            parameters=parameters,
            source_confidence=raw_data.get("confidence", 0.0)
        )
