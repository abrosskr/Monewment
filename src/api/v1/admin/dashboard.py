import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.dependencies import get_db
from src.models import User, Organization, Project, VMInstance, VMFlavor, VMUsage, Cluster
from src.schemas import ClusterCreateRequest, OrgApproveRequest, ProjectExpandRequest, PricingUpdateRequest
from src.core.logger import setup_logger
from src.core.security import validate_project_path
from src.collector import collector

logger = setup_logger()
router = APIRouter()

@router.get("/schema")
def get_real_db_schema():
    """[최적화] DB Inspector를 통해 실제 테이블 구조를 반환합니다."""
    return {"schema": collector.collect_db_schema()}

@router.get("/endpoints")
def get_real_api_endpoints():
    """[신규] FastAPI 라우트 정보를 실시간으로 추출하여 반환합니다."""
    return {"endpoints": collector.collect_api_endpoints()}

@router.get("/stats")
async def get_admin_stats(db: AsyncSession = Depends(get_db)):
    """관리자용 대시보드 통계 정보를 반환합니다."""
    total_users = await db.scalar(select(func.count(User.id)))
    total_projects = await db.scalar(select(func.count(Project.id)))
    active_vms = await db.scalar(select(func.count(VMInstance.id)).where(VMInstance.status == "RUNNING"))
    
    # 총 매출 계산 (단순 합계)
    total_revenue = await db.scalar(select(func.sum(VMUsage.total_cost))) or 0
    
    return {
        "users": total_users,
        "projects": total_projects,
        "active_vms": active_vms,
        "revenue": float(total_revenue)
    }

@router.get("/vms")
async def get_all_vms(db: AsyncSession = Depends(get_db)):
    """모든 프로젝트에서 실행 중인 VM 리스트를 반환합니다."""
    result = await db.execute(select(VMInstance))
    vms = result.scalars().all()
    
    result_list = []
    for vm in vms:
        result_list.append({
            "id": vm.id,
            "name": vm.name,
            "status": vm.status,
            "project_id": vm.project_id,
            "flavor": vm.flavor_id,
            "created_at": vm.created_at
        })
    return {"vms": result_list}

@router.get("/pricing/flavors")
async def get_flavors(db: AsyncSession = Depends(get_db)):
    """현재 등록된 VM 등급별 시간당 요금을 조회합니다."""
    result = await db.execute(select(VMFlavor))
    flavors = result.scalars().all()
    return {"flavors": [{"id": f.id, "name": f.name, "hourly_rate": float(f.hourly_rate)} for f in flavors]}

@router.patch("/pricing/flavors/{flavor_id}")
async def update_flavor_rate(flavor_id: int, req: PricingUpdateRequest, db: AsyncSession = Depends(get_db)):
    """특정 VM 등급의 시간당 요금을 실시간으로 업데이트합니다."""
    result = await db.execute(select(VMFlavor).where(VMFlavor.id == flavor_id))
    flavor = result.scalars().first()
    
    if not flavor:
        raise HTTPException(status_code=404, detail="Flavor not found")
    
    flavor.hourly_rate = req.hourly_rate
    await db.commit()
    return {"status": "success", "new_rate": float(flavor.hourly_rate)}

@router.get("/hierarchy")
async def get_system_hierarchy(db: AsyncSession = Depends(get_db)):
    """[최상위 관리자] 시스템 전체 계층 구조(Cluster -> Org -> Project)를 조회합니다."""
    try:
        stmt = select(Cluster).options(
            selectinload(Cluster.organizations).selectinload(Organization.projects)
        )
        result = await db.execute(stmt)
        clusters = result.scalars().all()
        
        cluster_list = []
        for c in clusters:
            orgs = []
            for org in c.organizations:
                projs = [{"id": p.id, "name": p.name, "status": p.status} for p in org.projects]
                orgs.append({
                    "id": org.id,
                    "name": org.name,
                    "status": org.status,
                    "projects": projs,
                    "quota": {"cpu": org.quota_cpu, "ram": org.quota_ram_gb, "gpu": org.quota_gpu}
                })
            cluster_list.append({
                "id": c.id,
                "name": c.name,
                "region": c.region,
                "status": c.status,
                "organizations": orgs
            })
        return {"hierarchy": cluster_list}
    except Exception as e:
        logger.error(f"Hierarchy Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clusters")
async def create_cluster(req: ClusterCreateRequest, db: AsyncSession = Depends(get_db)):
    """[최상위 관리자] 새 클러스터를 시스템에 등록합니다."""
    new_cluster = Cluster(
        name=req.name, 
        region=req.region, 
        cpu_capacity=req.cpu_capacity,
        ram_capacity_gb=req.ram_capacity_gb,
        gpu_capacity=req.gpu_capacity
    )
    db.add(new_cluster)
    await db.commit()
    return {"status": "success", "cluster_id": new_cluster.id}

@router.post("/organizations/approve")
async def approve_organization(req: OrgApproveRequest, db: AsyncSession = Depends(get_db)):
    """[최상위 관리자] 입점 신청한 Organization을 승인하고 자원을 할당합니다."""
    result = await db.execute(select(Organization).where(Organization.id == req.org_id))
    org = result.scalars().first()
    
    if not org: raise HTTPException(status_code=404, detail="Org not found")
    
    org.cluster_id = req.cluster_id
    org.quota_cpu = req.quota_cpu
    org.quota_ram_gb = req.quota_ram_gb
    org.quota_gpu = req.quota_gpu
    org.status = "ACTIVE"
    
    await db.commit()
    return {"status": "success"}

@router.post("/projects/expand")
async def expand_project_topdown(req: ProjectExpandRequest, db: AsyncSession = Depends(get_db)):
    """[최상위 관리자] 특정 Organization 하위에 프로젝트를 Top-Down 방식으로 직접 배포합니다."""
    # 1. 대상 Org 확인
    result = await db.execute(select(Organization).where(Organization.id == req.org_id))
    org = result.scalars().first()
    
    if not org: raise HTTPException(status_code=404, detail="Organization not found")
    
    # 2. 프로젝트 생성 (보안 검증 포함)
    target_path = validate_project_path(req.project_name)
    if os.path.exists(target_path):
        raise HTTPException(status_code=400, detail="이미 존재하는 프로젝트 폴더입니다.")
        
    # 물리 폴더 생성
    os.makedirs(target_path, exist_ok=True)
    
    # DB 기록
    new_project = Project(name=req.project_name, org_id=req.org_id, status="ACTIVE")
    db.add(new_project)
    await db.commit()
    
    return {"status": "success", "project_id": new_project.id, "path": str(target_path)}
