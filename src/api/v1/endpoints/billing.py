
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from src.dependencies import get_db
from src.services.billing import BillingService, PaymentGatewayError

router = APIRouter()

class ChargeRequest(BaseModel):
    project_id: int
    amount: float
    payment_token: str # Stripe Token (e.g. tok_visa)

class BalanceResponse(BaseModel):
    project_id: int
    prepaid_credits: float
    current_spend: float
    currency: str = "USD"

@router.post("/charge")
async def charge_project(req: ChargeRequest, db: AsyncSession = Depends(get_db)):
    """
    [Payment] Charge a card and top up project credits.
    """
    service = BillingService(db)
    try:
        payment = await service.charge_project(req.project_id, req.amount, req.payment_token)
        return {
            "status": "success",
            "transaction_id": payment.transaction_id,
            "amount_charged": payment.amount,
            "message": "Top-up successful"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PaymentGatewayError as e:
        raise HTTPException(status_code=402, detail=f"Payment Failed: {str(e)}")

@router.get("/balance/{project_id}", response_model=BalanceResponse)
async def get_balance(project_id: int, db: AsyncSession = Depends(get_db)):
    """
    Check current credits and spend.
    """
    service = BillingService(db)
    balance = await service.get_balance(project_id)
    
    return BalanceResponse(
        project_id=project_id,
        prepaid_credits=balance["prepaid_credits"],
        current_spend=balance["current_spend"]
    )
