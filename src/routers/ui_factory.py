# 파일 위치: src/routers/ui_factory.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import re
import logging

from src.dependencies import get_db
from src.models import User, Project, ProjectBudget, Organization

router = APIRouter(
    prefix="/api/v1/ui-factory",
    tags=["UI Factory (Monetization Core)"]
)

logger = logging.getLogger("UIFactory")

# 1. [상품 정의] 요청 받을 주문서 양식
class UIRequest(BaseModel):
    component_name: str
    spec_content: str
    api_key: str | None = None
    project_id: int | None = None # [Optional] Explicit project selection

# 2. [핵심 로직] UI 생성 엔진 (여기가 핵심 기술)
def generate_react_code(name: str, spec: str) -> str:
    # (1) 명세서 파싱 (기초적인 AI 흉내)
    width = "w-full"
    bg_color = "#1A1A1A"
    
    w_match = re.search(r"너비.*(\d+px|full)", spec)
    if w_match: width = f"w-[{w_match.group(1)}]" if "px" in w_match.group(1) else "w-full"
    
    bg_match = re.search(r"배경색.*(#[0-9a-fA-F]+)", spec)
    if bg_match: bg_color = bg_match.group(1)

    # (2) 코드 템플릿 조립
    return f"""'use client';

export default function {name}() {{
  return (
    // [Powered by Monewment UI Factory API]
    // 이 코드는 유료 생성 엔진에 의해 작성되었습니다.
    <div className="{width} h-full bg-[{bg_color}] flex flex-col p-4 border border-[#262626] text-white shadow-xl">
      <div className="flex justify-between items-center mb-4 border-b border-white/10 pb-2">
        <h2 className="text-lg font-bold text-[#FFD700]">{name}</h2>
        <span className="text-xs text-gray-500">Auto-Generated</span>
      </div>
      
      {{/* Dynamic Content Area */}}
      <div className="flex-1 bg-black/20 rounded border border-dashed border-[#404040] flex items-center justify-center">
        <span className="text-sm text-[#808080]">
           UI Factory Area ({width} x {bg_color})
        </span>
      </div>
    </div>
  );
}}
"""

async def process_billing(api_key: str, project_id: int | None, db: AsyncSession):
    """
    Validates API Key and deducts credit.
    Cost: $0.10 per generation
    """
    GENERATION_COST = 0.10
    
    # 1. Validate User
    if not api_key:
        raise HTTPException(status_code=401, detail="API Key required for billing.")
        
    res_user = await db.execute(select(User).where(User.api_key == api_key).options(selectinload(User.organization).selectinload(Organization.projects)))
    user = res_user.scalars().first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API Key.")
        
    # 2. Determine Project
    target_project = None
    
    if project_id:
        # Check if project belongs to user's org
        # Simplified: Assuming User belongs to Org, and Project belongs to SAME use's Org.
        # Strict RBAC would check ProjectMember, but for now check Org ownership.
        for p in user.organization.projects:
            if p.id == project_id:
                target_project = p
                break
        if not target_project:
             raise HTTPException(status_code=403, detail="Project not found or access denied.")
    else:
        # Auto-select first active project
        active_projects = [p for p in user.organization.projects if p.status == "ACTIVE"]
        if not active_projects:
            raise HTTPException(status_code=400, detail="No active projects found in your organization. Please create one.")
        target_project = active_projects[0]
        
    # 3. Deduct Budget
    # Find or Create Budget
    res_budget = await db.execute(select(ProjectBudget).where(ProjectBudget.project_id == target_project.id))
    budget = res_budget.scalars().first()
    
    if not budget:
        # Lazy Init
        budget = ProjectBudget(project_id=target_project.id, current_month_spend=0.0)
        db.add(budget)
        
    # Update Spend
    # Note: ProjectBudget.current_month_spend is defined as Numeric in models_append.txt but usage in metering.py implies float in SQLite?
    # src/models.py: Column(Numeric(10, 4), default=0)
    # We should cast to float for python math or keep Decimal. Let's cast to float for simplicity as per metering.py
    
    current_val = float(budget.current_month_spend or 0.0)
    budget.current_month_spend = current_val + GENERATION_COST
    
    await db.commit()
    
    logger.info(f"💰 Billing Success: Project {target_project.name} charged ${GENERATION_COST}")
    return target_project.name, GENERATION_COST


# 3. [판매 창구] API 엔드포인트
@router.post("/generate")
async def generate_ui(request: UIRequest, db: AsyncSession = Depends(get_db)):
    """
    [유료 API] 명세서를 보내면 React 코드를 반환합니다.
    (Cost: $0.10 per call)
    """
    # Billing Logic (Real)
    charged_project, cost = await process_billing(request.api_key, request.project_id, db)
    
    logger.info(f"💰 [UI Factory] Order Received: {request.component_name} (from {charged_project})")
    
    generated_code = generate_react_code(request.component_name, request.spec_content)
    
    return {
        "status": "success",
        "component_name": request.component_name,
        "billed_to": charged_project,
        "cost": cost,
        "code": generated_code,
    }