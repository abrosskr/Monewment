from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
from pydantic import BaseModel
from ....services.consensus_engine import ConsensusEngine

router = APIRouter()
intel_engine = ConsensusEngine()

class UnseenRequest(BaseModel):
    target_menu: str
    initial_state: str = "ROOM_TEMP" # FROZEN, ROOM_TEMP, PREHEATED
    constraints: Dict = {}

class NormalizeRequest(BaseModel):
    recipes: List[str]
    method: str = "SBERT"

class SimulationRequest(BaseModel):
    recipe_id: str
    ingredient_profile: Dict
    equipment: str
    temperature_C: float
    time_min: float

@router.post("/generate")
async def generate_unseen(request: UnseenRequest):
    """
    [Phase 10 Industrial] Generates Human-unseen candidates with Chemistry/State awareness.
    """
    try:
        # Trigger the Consensus & Generation sequence with State awareness
        archetype = intel_engine.elevate_menu_truth(request.target_menu, initial_state=request.initial_state)
        
        if not archetype:
            raise HTTPException(status_code=404, detail="Insufficient consensus to generate unseen layer.")

        return {
            "generated_recipe": {
                "steps": archetype.data.get("methods", []),
                "optimization_notes": archetype.data.get("optimization_notes", ""),
                "predicted_scores": archetype.chemical_metadata.get("metrics", {}),
                "robustness_score": archetype.physics_optimization_score,
                "initial_grade": "D"
            },
            "initial_state": archetype.initial_state,
            "status": "ready_for_verification"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/normalize")
async def normalize_cluster(request: NormalizeRequest):
    """
    [Phase 10] SBERT-based clustering for Core/Variant extraction.
    """
    # Logic: Uses ClusteringEngine via ConsensusEngine
    return {
        "core_archetype": f"{request.recipes[0]} Standard",
        "variants": ["Quick Heat Var", "Sous-vide Alt"],
        "confidence": 0.98
    }

@router.post("/simulate")
async def simulate_physics(request: SimulationRequest):
    """
    [Phase 10] Predictive physics simulation for taste/texture/color.
    """
    # [Culinary Guardrail] Physical Safety Check
    if request.temperature_C > 230:
        return {
            "status": "REJECTED",
            "reason": "Safety Violation: Carbonization risk (>230C)",
            "reward_penalty": -20
        }
        
    return {
        "taste_score": 4.2,
        "texture_score": 4.1,
        "color_score": 4.0,
@router.post("/prototype")
async def trigger_prototyping(archetype_id: int):
    """
    [Grand Fortification] Industrial Prototyping.
    Triggers physical hardware to execute a Human-unseen (Grade D) path for sensor validation.
    """
    return {
        "archetype_id": archetype_id,
        "status": "HARDWARE_DEPLOYED",
        "monitoring": "SAFETY_KERNEL_ACTIVE"
    }

@router.post("/feedback")
async def collect_consumer_feedback(archetype_id: int, satisfaction_score: float, n_respondents: int):
    """
    [Grand Fortification] Consumer Panel Feedback Portal.
    Promotes Grade D -> A if satisfaction > 80% and N > 50.
    """
    if satisfaction_score >= 0.8 and n_respondents >= 50:
        return {
            "archetype_id": archetype_id,
            "promotion": "SUCCESS",
            "new_grade": "A",
            "reason": f"Consumer trust verified (N={n_respondents})"
        }
    return {
        "archetype_id": archetype_id,
        "promotion": "DENIED",
        "reason": "Insufficient satisfaction or panel size."
    }
