from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict
from app.services.search_service import SearchService
from app.services.context_service import ContextService
from app.services.variant_service import VariantService

router = APIRouter()

class InventoryRequest(BaseModel):
    inventory: List[str]
    user_id: Optional[str] = None
    context: Optional[Dict[str, str]] = {}      # weather, mood
    user_profile: Optional[Dict[str, str]] = {} # authenticity_preference, convenience_preference

class RecipeMatch(BaseModel):
    recipe_name: str
    variant_name: str # [NEW]
    pivot_used: str
    completeness: float
    missing_count: int
    ingredients: List[str]
    score_boost: float # [NEW] to show why it was recommended

@router.post("/context", response_model=List[RecipeMatch])
def recommend_by_context(request: InventoryRequest):
    """
    Reverse Search + Context Boosting + Variant Selection.
    """
    # 1. Base Search (Logic Phase 1)
    base_results = SearchService.reverse_search(request.inventory)
    
    final_results = []
    
    for res in base_results:
        # 2. Context Boosting (Logic Phase 3)
        multiplier = ContextService.calculate_context_score(
            res["recipe_name"], 
            res["ingredients"], 
            request.context
        )
        
        # 3. Variant Selection (Logic Phase 3 - Dongpo Dilemma)
        variant = VariantService.select_variant(
            res["recipe_name"], 
            request.user_profile
        )
        
        # Apply Boost
        boosted_completeness = min(res["completeness"] * multiplier, 100.0)
        
        final_results.append({
            "recipe_name": res["recipe_name"],
            "variant_name": variant,
            "pivot_used": res["pivot_used"],
            "completeness": round(boosted_completeness, 1),
            "missing_count": res["missing_count"],
            "ingredients": res["ingredients"],
            "score_boost": round(multiplier, 2)
        })
        
    # Re-sort by new boosted score
    final_results.sort(key=lambda x: x["completeness"], reverse=True)
    
    return final_results
