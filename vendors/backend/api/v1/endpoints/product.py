from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.engines.product_standard.interface import ProductStandardInterface

router = APIRouter()

@router.get("/search", summary="Search Products (PIM)")
def search_products(
    q: str = Query(..., min_length=2, description="Product Name or Brand"),
    db: Session = Depends(get_db)
):
    """
    Search immutable product specs by name.
    """
    api = ProductStandardInterface(db)
    results = api.search_by_name(q)
    return results

@router.get("/{gtin}", summary="Get Product Spec (PIM)")
def get_product_spec(
    gtin: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed product specification (Physics, Nutrition).
    Does NOT return Price or Supplier info (use /logistics for that).
    """
    api = ProductStandardInterface(db)
    product = api.get_by_gtin(gtin)
    if not product:
        raise HTTPException(status_code=404, detail="Product Spec not found")
    return product
