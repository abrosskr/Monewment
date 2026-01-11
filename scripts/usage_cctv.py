
import sys
import os
import time
from datetime import datetime
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models import VMUsage, Project, ProjectSubscription, SubscriptionPlan, AIModel, VMInstance
from src.config import settings

# [Optimized] Global Engine (Singleton) - Connection Pool is handled by Engine
DB_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_engine(DB_URL, pool_size=5, max_overflow=5)
SessionLocal = sessionmaker(bind=engine)

def get_db_session():
    return SessionLocal()

def generate_dashboard():
    db = get_db_session()
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. Overview Stats (Fast Count)
        total_sessions = db.query(VMUsage).count()
        total_cost = float(db.query(func.sum(VMUsage.total_cost)).scalar() or 0.0)
        active_vms = db.query(VMInstance).filter(VMInstance.status == "RUNNING").count()
        
        # 2. Bulk Aggregation (Optimized: O(1) query instead of O(N))
        # Fetch all project costs in one go
        project_costs_query = db.query(
            VMInstance.project_id,
            func.sum(VMUsage.total_cost)
        ).join(VMInstance).group_by(VMInstance.project_id).all()
        
        # Convert to Dictionary map: {project_id: total_cost}
        project_cost_map = {pid: float(cost or 0.0) for pid, cost in project_costs_query}
        
        # Fetch all projects
        projects = db.query(Project).all()
        
        # 3. Engine Breakdown
        engine_usage = db.query(
            AIModel.name, 
            func.sum(VMUsage.total_cost),
            func.count(VMUsage.id)
        ).join(VMUsage, VMUsage.ai_model_id == AIModel.id).group_by(AIModel.name).all()

        markdown = f"""# 🎥 LIVE Usage Monitor (CCTV)
> **Last Updated:** {now} 🔴 LIVE

## 📊 System Overview
| Metric | Value |
| :--- | :--- |
| **Active VMs** | `{active_vms}` |
| **Total Sessions** | `{total_sessions}` |
| **Total Revenue** | `${total_cost:,.4f}` |

## 🏢 Project Status (Optimized)
"""
        
        markdown += "| Project | Plan | Credits | Used | Billable | Status |\n"
        markdown += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"

        for p in projects:
            p_credits = 0.0
            p_plan = "Free"
            if p.subscription and p.subscription.plan:
                p_credits = float(p.subscription.plan.monthly_credits)
                p_plan = p.subscription.plan.name
            
            # [Optimized] O(1) Access from Map
            p_spent = project_cost_map.get(p.id, 0.0)
            
            used_creds = min(p_spent, p_credits)
            billable = max(0.0, p_spent - p_credits)
            
            status_icon = "🟢"
            if p_spent > p_credits * 0.9: status_icon = "🟡"
            if p_spent > p_credits: status_icon = "🔴"
            
            markdown += f"| **{p.name}** | {p_plan} | ${p_credits:.2f} | ${p_spent:.4f} | **${billable:.4f}** | {status_icon} |\n"

        markdown += "\n## 🧠 Engine Usage (AI Models)\n"
        markdown += "| Model | Sessions | Total Cost |\n"
        markdown += "| :--- | :--- | :--- |\n"
        
        for name, cost, count in engine_usage:
            cost = float(cost or 0.0)
            markdown += f"| {name} | {count} | ${cost:.4f} |\n"
            
        # Add basic ASCII Chart for Cost Distribution if we have data
        if total_cost > 0:
            markdown += "\n## 📉 Real-time Cost Distribution\n"
            markdown += "```text\n"
            for name, cost, _ in engine_usage:
                cost = float(cost or 0.0)
                percent = int((cost / total_cost) * 20)
                bar = "█" * percent
                markdown += f"{name.ljust(15)} | {bar} ${cost:.2f}\n"
            markdown += "```\n"

        return markdown

    finally:
        db.close()

def run_loop():
    target_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "LIVE_USAGE.md")
    print(f"🎥 CCTV Started. Modeling to: {target_file}")
    print("Press Ctrl+C to stop.")
    
    while True:
        try:
            content = generate_dashboard()
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(content)
            time.sleep(2) # Update every 2 seconds
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error updating Dashboard: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_loop()
