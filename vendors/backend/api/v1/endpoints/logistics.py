from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.engines.logistics.models import ProductSourcing, Supplier, ProductBatch

router = APIRouter()

@router.get("/offers/{gtin}", summary="Get Market Offers (SCM)")
def get_offers(
    gtin: str,
    db: Session = Depends(get_db)
):
    """
    Get all active logistics offers for a specific Product GTIN.
    Returns Cost, Supplier, and Fulfillment Type.
    """
    offers = db.query(ProductSourcing).filter(
        ProductSourcing.product_gtin == gtin, 
        ProductSourcing.is_active == True
    ).all()
    
    return [
        {
            "id": o.sourcing_id,
            "supplier": o.supplier.name,
            "fulfillment": o.fulfillment_type,
            "cost": o.cost_price_vat_exclusive,
            "moq": o.moq,
            "lead_time": o.lead_time_days
        }
        for o in offers
    ]

@router.get("/inventory/{gtin}", summary="Check Local Inventory")
def check_inventory(
    gtin: str,
    db: Session = Depends(get_db)
):
    """
    Check currently held batches (Owned Inventory) for this GTIN.
    """
    # Join Sourcing to filter by GTIN
    batches = db.query(ProductBatch).join(ProductSourcing).filter(
        ProductSourcing.product_gtin == gtin,
        ProductBatch.current_quantity > 0
    ).all()
    
    return [
        {
            "batch_id": b.batch_id,
            "qty": b.current_quantity,
            "expiry": b.expiration_date
        }
        for b in batches
    ]
