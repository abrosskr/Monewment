from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel 
from typing import List, Optional
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.dependencies import get_db
from src.models import VMInstance, VMFlavor, VMUsage, AIModel, Project

# [Phase 3] K8s Client Import (Replaced by ClusterManager in Phase 4.6)

router = APIRouter()
logger = logging.getLogger(__name__)

# --- Models ---
class VMCreateRequest(BaseModel):
    name: str # VM Name
    flavor_id: int # H/W Spec
    ai_model_id: Optional[int] = None # S/W Spec
    project_id: int # Project ID

class VMSwitchModelRequest(BaseModel):
    new_model_id: int

class VMStatusResponse(BaseModel):
    id: int
    name: str
    status: str
    flavor_name: str
    current_cost: float
    ip: Optional[str] = None

# --- Helpers ---
def calculate_cost(usage: VMUsage, end_time: datetime) -> float:
    duration = (end_time - usage.start_time).total_seconds()
    hours = duration / 3600.0
    rate = float(usage.applied_hw_rate) + float(usage.applied_model_rate)
    return round(hours * rate, 4)

# --- Endpoints ---

@router.get("", response_model=List[VMStatusResponse])
async def list_vms(db: AsyncSession = Depends(get_db)):
    """List all VMs from Database."""
    result = await db.execute(select(VMInstance).options(selectinload(VMInstance.flavor)))
    vms = result.scalars().all()
    results = []
    
    for vm in vms:
        # Calculate real-time cost for active session
        current_cost = 0.0
        # Check usage
        usage_res = await db.execute(select(VMUsage).where(
            VMUsage.vm_id == vm.id, 
            VMUsage.end_time.is_(None)
        ))
        active_usage = usage_res.scalars().first()
        
        if active_usage:
            # Note: start_time in DB should be timezone aware or UTC. Assuming UTC.
            now = datetime.now(timezone.utc)
            # Ensure start_time is treated as UTC
            start_utc = active_usage.start_time.replace(tzinfo=timezone.utc) if active_usage.start_time.tzinfo is None else active_usage.start_time
            
            duration = (now - start_utc).total_seconds()
            rate = float(active_usage.applied_hw_rate) + float(active_usage.applied_model_rate)
            current_cost = (duration / 3600.0) * rate

        results.append(VMStatusResponse(
            id=vm.id,
            name=vm.name,
            status=vm.status,
            flavor_name=vm.flavor.name if vm.flavor else "Unknown",
            current_cost=round(current_cost, 4),
            ip=None # TODO: Fetch from KubeVirt logic if needed
        ))
    return results

@router.post("", response_model=VMStatusResponse)
async def create_vm(req: VMCreateRequest, db: AsyncSession = Depends(get_db)):
    """Create VM: DB Record -> Usage Start -> KubeVirt/Stub Launch"""
    
    # 1. Validation
    res_flav = await db.execute(select(VMFlavor).where(VMFlavor.id == req.flavor_id))
    flavor = res_flav.scalars().first()
    if not flavor:
        raise HTTPException(status_code=404, detail="Flavor not found")
        
    ai_model = None
    if req.ai_model_id:
        res_ai = await db.execute(select(AIModel).where(AIModel.id == req.ai_model_id))
        ai_model = res_ai.scalars().first()
        if not ai_model:
            raise HTTPException(status_code=404, detail="AI Model not found")
            
    # 2. [Hybrid Model] Check Budget/Burst Eligibility
    from src.models import ProjectBudget, ProjectSubscription
    
    # query subscription
    res_sub = await db.execute(select(ProjectSubscription).where(ProjectSubscription.project_id == req.project_id).options(selectinload(ProjectSubscription.plan)))
    sub = res_sub.scalars().first()
    
    if sub:
        # Check Budget
        res_budget = await db.execute(select(ProjectBudget).where(ProjectBudget.project_id == req.project_id))
        budget = res_budget.scalars().first()
        current_spend = float(budget.current_month_spend) if budget else 0.0
        
        # Hard Cap
        if sub.usage_limit_hard_cap is not None:
            if current_spend >= float(sub.usage_limit_hard_cap):
                raise HTTPException(status_code=402, detail=f"Project Budget Exceeded (Hard Cap: ${sub.usage_limit_hard_cap})")
        
        # Burst Check
        credits = float(sub.plan.monthly_credits) if sub.plan else 0.0
        if current_spend >= credits:
            if not sub.allow_burst:
                raise HTTPException(status_code=402, detail="Credits Exhausted. Enable Burst Mode to continue.")
            else:
                logger.info(f"⚠️ Burst Mode Entry: VM {req.name} allowed via Overdraft.")
    
    # 3. Create VM Record
            
    # 2. [Hybrid Model] Check Budget/Burst Eligibility
    # Need synchronous session for MeteringService? The service is written with sync session in mind (db.query).
    # But here 'db' is AsyncSession. 
    # We should refactor MeteringService to use 'select' (Async) OR instantiate it differently.
    # Quick fix: Copy logic or make MeteringService async-compatible.
    # Since MeteringService was written in Phase 4 as Sync, we should probably stick to Async patterns here in the endpoint
    # to avoid blocking the loop.
    
    # We will implement the check logic directly here using Async patterns for performance and correctness in FastAPI async path.
    from src.models import ProjectBudget, ProjectSubscription
    
    # query subscription
    res_sub = await db.execute(select(ProjectSubscription).where(ProjectSubscription.project_id == req.project_id).options(selectinload(ProjectSubscription.plan)))
    sub = res_sub.scalars().first()
    
    if sub:
        # Check Budget
        res_budget = await db.execute(select(ProjectBudget).where(ProjectBudget.project_id == req.project_id))
        budget = res_budget.scalars().first()
        current_spend = float(budget.current_month_spend) if budget else 0.0
        
        # Hard Cap
        if sub.usage_limit_hard_cap is not None:
            if current_spend >= float(sub.usage_limit_hard_cap):
                raise HTTPException(status_code=402, detail=f"Project Budget Exceeded (Hard Cap: ${sub.usage_limit_hard_cap})")
        
        # Burst Check
        credits = float(sub.plan.monthly_credits) if sub.plan else 0.0
        if current_spend >= credits:
            if not sub.allow_burst:
                raise HTTPException(status_code=402, detail="Credits Exhausted. Enable Burst Mode to continue.")
            else:
                logger.info(f"⚠️ Burst Mode Entry: VM {req.name} allowed via Overdraft.")
    
    # 3. Create VM Record

    # 2. Check for Duplicates
    res_dup = await db.execute(select(VMInstance).where(VMInstance.name == req.name))
    if res_dup.scalars().first():
        raise HTTPException(status_code=400, detail="VM name already exists")

    # 3. Create VM Record
    new_vm = VMInstance(
        name=req.name,
        project_id=req.project_id,
        flavor_id=req.flavor_id,
        status="PROVISIONING"
    )
    db.add(new_vm)
    await db.commit()
    await db.refresh(new_vm)

    # 4. Start Metering (Usage Session)
    usage = VMUsage(
        vm_id=new_vm.id,
        ai_model_id=req.ai_model_id,
        start_time=datetime.now(timezone.utc),
        applied_hw_rate=flavor.hourly_rate,
        applied_model_rate=ai_model.hourly_surcharge if ai_model else 0.0
    )
    db.add(usage)
    await db.commit()

    # 5. Launch Infrastructure (Stub or KubeVirt)
    try:
        # [Phase 4.6] Multi-Cluster Dynamic Routing
        # Fetch Project & Org Info to determine Cluster
        from src.core.cluster_manager import ClusterManager
        from src.models import Project
        
        # We need to reload project with organization info (optimization: could be done earlier)
        res_proj = await db.execute(
            select(Project).options(selectinload(Project.organization))
            .where(Project.id == req.project_id)
        )
        project = res_proj.scalars().first()
        
        # Get appropriate K8s Client for this Project's Cluster
        manager = ClusterManager.get_instance()
        k8s_client = manager.get_client_by_project(project)
        
        if k8s_client:
            # Prod/Dev with KubeVirt (Targeted Cluster)
            vmi_manifest = {
                "apiVersion": "kubevirt.io/v1",
                "kind": "VirtualMachineInstance",
                "metadata": {"name": req.name},
                "spec": {
                    "domain": {
                        "devices": {"disks": [{"name": "containerdisk", "disk": {"bus": "virtio"}}]},
                        "resources": {"requests": {"memory": f"{flavor.memory_gb}G"}}
                    },
                    "volumes": [{"name": "containerdisk", "containerDisk": {"image": "quay.io/kubevirt/cirros-container-disk-demo"}}]
                }
            }
            # Use the specific client's custom_api
            k8s_client.custom_api.create_namespaced_custom_object("kubevirt.io", "v1", "default", "virtualmachineinstances", vmi_manifest)
            logger.info(f"Deployed VM {req.name} to Cluster ID: {project.organization.cluster_id if project and project.organization else 'Default'}")
        else:
            # Stub Mode (No KubeVirt Client or intentional Stub)
            logger.info("Running in STUB MODE: Skipping actual KubeVirt creation.")
        
        # update status
        new_vm.status = "RUNNING"
        await db.commit()
        
    except Exception as e:
        logger.error(f"VM Creation Failed: {e}")
        # Rollback Usage
        await db.delete(usage)
        await db.delete(new_vm)
        await db.commit()
        raise HTTPException(status_code=500, detail=str(e))

    return VMStatusResponse(
        id=new_vm.id, name=new_vm.name, status=new_vm.status,
        flavor_name=flavor.name, current_cost=0.0
    )

@router.delete("/{name}")
async def delete_vm(name: str, db: AsyncSession = Depends(get_db)):
    """Stop VM: Stop Usage -> Calculate Cost -> Terminate Infra"""
    res_vm = await db.execute(select(VMInstance).where(VMInstance.name == name))
    vm = res_vm.scalars().first()
    if not vm:
        raise HTTPException(status_code=404, detail="VM not found")
        
    # 1. Stop Metering
    res_usage = await db.execute(select(VMUsage).where(VMUsage.vm_id == vm.id, VMUsage.end_time.is_(None)))
    active_usage = res_usage.scalars().first()
    
    if active_usage:
        now = datetime.now(timezone.utc)
        active_usage.end_time = now
        
        # Calculate Cost
        start_utc = active_usage.start_time.replace(tzinfo=timezone.utc) if active_usage.start_time.tzinfo is None else active_usage.start_time
        duration = (now - start_utc).total_seconds()
        active_usage.duration_seconds = int(duration)
        
        rate = float(active_usage.applied_hw_rate) + float(active_usage.applied_model_rate)
        cost = (duration / 3600.0) * rate
        active_usage.total_cost = round(cost, 4)
        
        await db.commit()

    # 2. Terminate Infra
    # [Phase 4.6] Multi-Cluster Dynamic Routing
    from src.core.cluster_manager import ClusterManager
    
    # Needs Project info to find cluster
    # vm.project_id is available
    res_proj = await db.execute(
        select(Project).options(selectinload(Project.organization))
        .where(Project.id == vm.project_id)
    )
    project = res_proj.scalars().first()
    
    manager = ClusterManager.get_instance()
    k8s_client = manager.get_client_by_project(project)
    
    if k8s_client:
        try:
            k8s_client.custom_api.delete_namespaced_custom_object("kubevirt.io", "v1", "default", "virtualmachineinstances", name)
        except Exception as e:
            logger.warning(f"KubeVirt delete failed (might be stub): {e}")

    # 3. Update DB
    vm.status = "TERMINATED"
    await db.commit()

    return {"status": "success", "message": f"VM {name} terminated. Cost recorded."}

@router.post("/{name}/switch_model")
async def switch_model(name: str, req: VMSwitchModelRequest, db: AsyncSession = Depends(get_db)):
    """Dynamic Billing: Close current usage -> Start new usage with new rate"""
    res_vm = await db.execute(select(VMInstance).options(selectinload(VMInstance.flavor)).where(VMInstance.name == name))
    vm = res_vm.scalars().first()
    if not vm:
        raise HTTPException(status_code=404, detail="VM not found")
        
    res_new = await db.execute(select(AIModel).where(AIModel.id == req.new_model_id))
    new_model = res_new.scalars().first()
    if not new_model:
        raise HTTPException(status_code=404, detail="Model not found")
        
    # 1. Close active usage
    res_usage = await db.execute(select(VMUsage).where(VMUsage.vm_id == vm.id, VMUsage.end_time.is_(None)))
    active_usage = res_usage.scalars().first()
    
    if active_usage:
        now = datetime.now(timezone.utc)
        active_usage.end_time = now
        
        # Calc cost
        start_utc = active_usage.start_time.replace(tzinfo=timezone.utc) if active_usage.start_time.tzinfo is None else active_usage.start_time
        duration = (now - start_utc).total_seconds()
        active_usage.duration_seconds = int(duration)
        rate = float(active_usage.applied_hw_rate) + float(active_usage.applied_model_rate)
        active_usage.total_cost = round((duration / 3600.0) * rate, 4)
        
    # 2. Start new usage
    # Keep same Hardware Flavor rate
    hw_rate = active_usage.applied_hw_rate if active_usage else vm.flavor.hourly_rate
    
    new_usage = VMUsage(
        vm_id=vm.id,
        ai_model_id=new_model.id,
        start_time=datetime.now(timezone.utc),
        applied_hw_rate=hw_rate,
        applied_model_rate=new_model.hourly_surcharge
    )
    db.add(new_usage)
    await db.commit()
    
    return {"status": "success", "message": f"Switched to model {new_model.name}. Billing rate updated."}
