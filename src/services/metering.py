
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone

from src.models import VMUsage, VMInstance, AIModel, VMFlavor, ProjectBudget, ProjectSubscription, Project

class MeteringService:
    def __init__(self, db: Session):
        self.db = db

    def start_session(self, vm_id: int, ai_model_id: int = None) -> VMUsage:
        """
        Starts a new metering session.
        If a session is already active for this VM, it should be closed first (caller responsibility).
        Snapshots current pricing.
        """
        vm = self.db.query(VMInstance).get(vm_id)
        if not vm:
            raise ValueError(f"VM {vm_id} not found")

        # Snapshot Hardware Rate
        hw_rate = vm.flavor.hourly_rate

        # Snapshot AI Model Rate
        model_rate = 0.0
        if ai_model_id:
            model = self.db.query(AIModel).get(ai_model_id)
            if model:
                model_rate = model.hourly_surcharge

        new_usage = VMUsage(
            vm_id=vm_id,
            ai_model_id=ai_model_id,
            start_time=datetime.now(timezone.utc),
            applied_hw_rate=hw_rate,
            applied_model_rate=model_rate,
            total_cost=0.0
        )
        self.db.add(new_usage)
        self.db.commit()
        self.db.refresh(new_usage)
        return new_usage

    def end_session(self, vm_id: int) -> VMUsage:
        """
        Ends the currently active session for a VM.
        Calculates final cost based on duration.
        """
        # Find active session (end_time is Null)
        usage = self.db.query(VMUsage).filter(
            VMUsage.vm_id == vm_id,
            VMUsage.end_time == None
        ).order_by(VMUsage.start_time.desc()).first()

        if not usage:
            return None # No active session to end

        end_time = datetime.now(timezone.utc)
        
        # Ensure timezone awareness for subtraction
        start_time = usage.start_time
        if start_time.tzinfo is None:
            # Fallback if DB didn't save tzinfo (SQLite doesn't natively)
            # Assuming DB stores UTC naively
            start_time = start_time.replace(tzinfo=timezone.utc)
            
        duration = (end_time - start_time).total_seconds()
        duration_hours = duration / 3600.0

        total_rate = float(usage.applied_hw_rate) + float(usage.applied_model_rate)
        cost = total_rate * duration_hours

        # Update Record
        usage.end_time = end_time
        usage.duration_seconds = int(duration)
        usage.total_cost = round(cost, 6) 

        self.db.commit()
        self.db.refresh(usage)
        
        # Update Project Budget Cache (Optional Optimization)
        self._update_project_spend(usage.vm.project_id, cost)
        
        return usage

    def _update_project_spend(self, project_id: int, added_cost: float):
        """
        Increments the current_month_spend in ProjectBudget
        """
        budget = self.db.query(ProjectBudget).filter(ProjectBudget.project_id == project_id).first()
        if budget:
            budget.current_month_spend = float(budget.current_month_spend) + added_cost
            self.db.commit()

    def get_project_current_usage(self, project_id: int) -> dict:
        """
        Returns {
            "total_spend": 120.50,
            "credits": 50.00,
            "used_credits": 50.00,
            "billable": 70.50
        }
        """
        project = self.db.query(Project).get(project_id)
        if not project:
            return {}

        total_spend = 0.0
        
        # Calculate from raw logs (More accurate than cache for now)
        # In production key, use cache + active sessions
        usage_query = self.db.query(
            func.sum(VMUsage.total_cost)
        ).join(VMInstance).filter(VMInstance.project_id == project_id)
        
        result = usage_query.scalar()
        if result:
            total_spend = float(result)

        credits = 0.0
        if project.subscription and project.subscription.plan:
             credits = float(project.subscription.plan.monthly_credits)

        used_credits = min(total_spend, credits)
        billable = max(0.0, total_spend - credits)

        return {
            "total_spend": round(total_spend, 4),
            "credits": round(credits, 2),
            "used_credits": round(used_credits, 4),
            "billable": round(billable, 4)
        }

    def check_eligibility(self, project_id: int) -> tuple[bool, str]:
        """
        [Hybrid Model Logic]
        Checks if a project can start new resources (VMs/AI) based on budget & burst settings.
        Returns (is_allowed, reason)
        """
        project = self.db.query(Project).get(project_id)
        if not project:
            return False, "Project not found"
            
        # 1. Check Hard Cap (Safety Latch)
        # If no subscription, assume Free Tier logic (might block or allow small)
        # For this implementation, we require subscription for advanced logic, else allow (Default Open)
        if not project.subscription:
            return True, "No subscription (Default Allowed)"
            
        sub = project.subscription
        # Get Budget Cache (faster than full sum)
        budget = self.db.query(ProjectBudget).filter(ProjectBudget.project_id == project_id).first()
        current_spend = float(budget.current_month_spend) if budget else 0.0
        
        # Hard Cap Check
        if sub.usage_limit_hard_cap is not None:
             limit = float(sub.usage_limit_hard_cap)
             if current_spend >= limit:
                 return False, f"Budget Hard Cap Reached (${limit})"
        
        # 2. Check Credits vs Burst
        credits = float(sub.plan.monthly_credits) if sub.plan else 0.0
        
        if current_spend < credits:
            return True, "Within Credits"
            
        # 3. Over-Quota Logic
        if sub.allow_burst:
             return True, f"Burst Mode Active (Multiplier x{sub.burst_multiplier})"
        else:
             return False, "Credits Exhausted & Burst Disabled"
