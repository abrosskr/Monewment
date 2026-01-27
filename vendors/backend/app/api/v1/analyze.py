from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.services.normalizer_service import RecipeNormalizer
from app.services.auto_labeler import AutoLabeler

router = APIRouter()

class TextRequest(BaseModel):
    text: str

from app.services.extractor_service import ExtractorService
from app.core.fis_physics import FisPhysics
from typing import Optional

class IngredientStructured(BaseModel):
    name: str
    amount: Optional[float]
    unit: Optional[str]

class AnalysisResponse(BaseModel):
    method: str
    culture: str
    target_temp: float
    physics_goal: str
    reaction_probability: float # [Sophisticated]
    ingredients: List[IngredientStructured] = [] # [Expansion]
    ingredient_physics: Dict[str, Any] = {} # [Hardening]

@router.post("/text", response_model=AnalysisResponse)
def analyze_text(request: TextRequest):
    """
    Analyzes raw recipe text using AI Extraction + Physics Engine.
    """
    # 1. AI Semantic Extraction
    extraction = ExtractorService.extract_entities(request.text)
    method = extraction["method"]
    extracted_ingredients = extraction["ingredients"]
    
    # 2. Extract Logic (Legacy/Support)
    # We still use words for culture prediction for now
    words = request.text.split()
    culture = AutoLabeler.predict_culture(words)
    context = RecipeNormalizer.analyze_context(method, words)
    
    # 3. [Hardening] Physical Property Extraction (from structured names)
    detected_physics = {}
    for ing in extracted_ingredients:
        name = ing["name"]
        props = FisPhysics.get_physics_properties(name)
        
        # Check if it's a known ingredient in our DB
        is_known = False
        for k in FisPhysics.PHYSICS_DB.keys():
            if k in name.lower():
                is_known = True
                break
        
        if is_known:
            detected_physics[name] = props

    return {
        "method": method,
        "culture": culture,
        "target_temp": context["target_temp"],
        "physics_goal": context["physics_goal"],
        "reaction_probability": context["reaction_probability"],
        "ingredients": extracted_ingredients,
        "ingredient_physics": detected_physics
    }
