from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict
from ..services.fis_service import FisService
from ..core.security import get_api_key

router = APIRouter(prefix="/fis", tags=["FIS (Printer)"])

def get_fis_service():
    return FisService()

class TargetFlavor(BaseModel):
    vector: List[float] # [Salt, Sweet, Umami, Spicy, Sour]

class InkRecipe(BaseModel):
    status: str
    recipe: Dict[str, float]
    simulated_taste: List[float]
    error_rate: float

@router.post("/optimize", response_model=InkRecipe)
def calculate_ink_recipe(
    target: TargetFlavor, 
    _ = Depends(get_api_key),
    service: FisService = Depends(get_fis_service)
):
    """
    [FIS Engine] Calculate optimal ink mixture for target flavor.
    Input: [Salt, Sweet, Umami, Spicy, Sour]
    Requires: X-API-KEY header
    """
    try:
        result = service.optimize_recipe(target.vector)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/inks")
def get_available_inks(service: FisService = Depends(get_fis_service)):
    """
    Get specifications of currently loaded inks.
    """
    return service.get_ink_list()
