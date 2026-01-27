from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

# Import services
from ..services.memory_service import MemoryService
from ..services.recipe_cache import recipe_cache

router = APIRouter(prefix="/training", tags=["training"])

# Singletons
memory = MemoryService()

class TrainingData(BaseModel):
    menu_name: str
    ingredients: List[dict]
    classification: dict

class ClassificationResult(BaseModel):
    food_type_name: str
    base_material: str
    default_method: str
    protein_modifier: str # e.g. "Fish" (Category)
    protein_part: Optional[str] = "Whole" # e.g. "Canned" (Part)
    main_ingredient_source: Optional[str] = None # e.g. "Canned Tuna" (Actual Input)
    primary_modifier: str
    primary_flavor: Optional[str] = None
    secondary_flavor: Optional[str] = None
    reasoning: Optional[str] = None

@router.get("/next")
def get_next_training_item():
    """
    사전 분류된 레시피를 즉시 반환합니다.
    백그라운드에서 이미 분류된 데이터를 사용하여 즉시 응답합니다.
    """
    try:
        # 1. 분류된 레시피 우선 가져오기 (즉시 반환!)
        target = recipe_cache.get_recipe_with_classification()
        if not target:
            raise HTTPException(status_code=404, detail="No recipes available. Please wait for cache to fill.")
        
        # 2. FILTER tools from the ingredient list before returning to UI
        from ..services.ontology_normalization import OntologyService
        raw_ingredients = target.get('ingredients', [])
        filtered_ingredients = OntologyService.filter_ingredients(raw_ingredients)
        
        # 3. 이미 분류되어 있으면 그대로 사용, 아니면 None
        prediction = target.get('classification')
        
        # [IMPROVEMENT] if prediction exists but protein_modifier is empty, try to guess it
        # or if no prediction, create a partial one
        if not prediction:
            prediction = {}
            
        if not prediction.get('protein_modifier'):
            guessed_main = OntologyService.predict_main_ingredient(target.get('name', ''), filtered_ingredients)
            if guessed_main:
                prediction['protein_modifier'] = guessed_main

        if not prediction.get('primary_flavor'):
            guessed_flavor = OntologyService.predict_flavor(target.get('name', ''), filtered_ingredients)
            if guessed_flavor:
                prediction['primary_flavor'] = guessed_flavor
                
        # 4. 캐시 상태도 함께 반환
        cache_status = recipe_cache.get_cache_status()
        
        return {
            "recipe": {
                "url": target.get('url'),
                "name": target.get('name'),
                "ingredients": filtered_ingredients,
                "image": target.get('image')
            },
            "prediction": prediction,
            "cache_status": cache_status,
            "pre_classified": target.get('classified', False) # Check explicit flag
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache/status")
def get_cache_status():
    """캐시 상태 확인"""
    return recipe_cache.get_cache_status()

@router.post("/cache/prefill")
def prefill_cache(count: int = 10):
    """캐시 수동으로 미리 채우기"""
    return recipe_cache.prefill(count)

@router.post("/cache/force-daily")
def force_daily_collect(target: int = 50):
    """강제로 일일 수집 시작 (백그라운드)"""
    return recipe_cache.force_daily_collect(target)

@router.post("/cache/start-worker")
def start_classification_worker():
    """백그라운드 분류 워커 시작"""
    return recipe_cache.start_background_classification()

@router.get("/search/ingredient")
def search_recipe_by_ingredient(q: str):
    """
    [Intelligent Service] 재료 기반 레시피 검색
    Query: "돼지고기, 김치" -> Vector Search -> Recipes
    """
    from app.services.memory_service import MemoryService
    mem = MemoryService()
    ingredients = [x.strip() for x in q.split(",")]
    results = mem.search_by_ingredients(ingredients, k=5)
    return {"query": ingredients, "results": results}

@router.post("/save")
def save_golden_record(data: TrainingData):
    """
    Saves the User-Corrected data into the RAG Memory.
    """
    try:
        # Construct the text representation typical for RAG
        # "MenuName (Ing: A, B, C)"
        ing_text = ", ".join([i['item'] for i in data.ingredients])
        full_text = f"{data.menu_name} ({ing_text})"
        
        # Save to Memory
        memory.add_memory(full_text, data.classification)
        
        return {"status": "success", "message": "Golden Record Saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
