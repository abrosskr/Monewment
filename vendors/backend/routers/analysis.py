from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.normalizer_service import RecipeNormalizer
from app.services.auto_labeler import AutoLabeler
from app.services.extractor_service import ExtractorService
from app.core.fis_physics import FisPhysics
from app.core.security import get_api_key
from app.core.logging import logger

router = APIRouter(prefix="/analysis", tags=["Analysis"], dependencies=[Depends(get_api_key)])

class TextRequest(BaseModel):
    text: str

class IngredientStructured(BaseModel):
    name: str
    amount: Optional[float]
    unit: Optional[str]

class AnalysisResponse(BaseModel):
    method: str
    culture: str
    target_temp: float
    physics_goal: str
    reaction_intensity: float
    core_temp_predicted: float = 25.0
    overcook_risk: float = 0.0
    ingredients: List[IngredientStructured] = []
    ingredient_physics: Dict[str, Any] = {}

def get_normalizer():
    return RecipeNormalizer()

def get_extractor():
    return ExtractorService()

@router.post("/text", response_model=AnalysisResponse)
def analyze_text(
    request: TextRequest,
    _ = Depends(get_api_key),
    extractor: ExtractorService = Depends(get_extractor),
    normalizer: RecipeNormalizer = Depends(get_normalizer)
):
    """
    [Hardened] Analyzes raw recipe text using AI Extraction + Physics Engine.
    Requires: X-API-KEY header
    """
    logger.info(f"🔍 Analyzing recipe text: {request.text[:50]}...")
    
    # 1. AI Semantic Extraction
    extraction = extractor.extract_entities(request.text)
    method = extraction.get("method", "Unknown")
    extracted_ingredients = extraction.get("ingredients", [])
    
    # 2. Extract Logic (Legacy/Support)
    words = request.text.split()
    culture = AutoLabeler.predict_culture(words)
    context = normalizer.analyze_context(method, [i['name'] for i in extracted_ingredients])
    
    # 3. [Hardening] Physical Property Extraction
    detected_physics = {}
    for ing in extracted_ingredients:
        name = ing["name"]
        props = FisPhysics.get_physics_properties(name)
        
        # Check if it's a known ingredient in our DB
        is_known = False
        fis_physics_db = FisPhysics.PHYSICS_DB or {} # Ensure it's not None
        for k in fis_physics_db.keys():
            if k in name.lower():
                is_known = True
                break
        
        if is_known:
            detected_physics[name] = props

    logger.info(f"✅ Analysis complete. Detected method: {method}, Culture: {culture}")
    
    return {
        "method": method,
        "culture": culture,
        "target_temp": context["target_temp"],
        "physics_goal": context["physics_goal"],
        "reaction_intensity": context["reaction_intensity"],
        "core_temp_predicted": context["core_temp_estimate"],
        "overcook_risk": context["overcook_risk"],
        "ingredients": extracted_ingredients,
        "ingredient_physics": detected_physics
    }
