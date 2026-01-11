
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import ProjectBudget, PaymentHistory, Project

class PaymentGatewayError(Exception):
    pass

class BillingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def charge_project(self, project_id: int, amount: float, payment_token: str) -> PaymentHistory:
        """
        [Mock Payment] Charges the user via Stripe-like token and tops up credits.
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        # Async Query
        res_proj = await self.db.execute(select(Project).where(Project.id == project_id))
        project = res_proj.scalars().first()
        if not project:
            raise ValueError("Project not found")

        # 1. Simulate PG Call (Stripe)
        transaction_id = self._mock_process_payment(amount, payment_token)
        
        # 2. Record Transaction
        payment = PaymentHistory(
            project_id=project_id,
            transaction_id=transaction_id,
            amount=amount,
            status="SUCCESS",
            payment_method="card_mock"
        )
        self.db.add(payment)
        
        # 3. Top-Up Budget (Prepaid Credits)
        # Find or Create Budget
        res_budget = await self.db.execute(select(ProjectBudget).where(ProjectBudget.project_id == project_id))
        budget = res_budget.scalars().first()
        
        if not budget:
            budget = ProjectBudget(project_id=project_id, current_month_spend=0.0, prepaid_credits=0.0)
            self.db.add(budget)
            
        current_prepaid = float(budget.prepaid_credits or 0.0)
        budget.prepaid_credits = current_prepaid + amount
        
        await self.db.commit()
        await self.db.refresh(payment)
        
        return payment

    def _mock_process_payment(self, amount: float, token: str) -> str:
        """
        Simulates interacting with Stripe API.
        returns: transaction_id
        raises: PaymentGatewayError
        """
        # Test Logic
        if token == "tok_fail":
            raise PaymentGatewayError("Card declined")
            
        # Success
        return f"pi_mock_{uuid.uuid4().hex[:12]}"

    async def get_balance(self, project_id: int) -> dict:
        res = await self.db.execute(select(ProjectBudget).where(ProjectBudget.project_id == project_id))
        budget = res.scalars().first()
        
        if not budget:
            return {"prepaid_credits": 0.0, "current_spend": 0.0}
            
        return {
            "prepaid_credits": float(budget.prepaid_credits or 0.0),
            "current_spend": float(budget.current_month_spend or 0.0)
        }
