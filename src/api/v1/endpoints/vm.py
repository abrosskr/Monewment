from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel 
from typing import List, Optional
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from src.dependencies import get_db
from src.models import VMInstance, VMFlavor, VMUsage, AIModel, Project

# [Phase 3] K8s Client Import
try:
    from src.core.k8s_client import k8s
except ImportError:
    k8s = None

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
def list_vms(db: Session = Depends(get_db)):
    """List all VMs from Database."""
    vms = db.query(VMInstance).all()
    results = []
    
    for vm in vms:
        # Calculate real-time cost for active session
        current_cost = 0.0
        active_usage = db.query(VMUsage).filter(VMUsage.vm_id == vm.id, VMUsage.end_time.is_(None)).first()
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
def create_vm(req: VMCreateRequest, db: Session = Depends(get_db)):
    """Create VM: DB Record -> Usage Start -> KubeVirt/Stub Launch"""
    
    # 1. Validation
    flavor = db.query(VMFlavor).filter(VMFlavor.id == req.flavor_id).first()
    if not flavor:
        raise HTTPException(status_code=404, detail="Flavor not found")
        
    ai_model = None
    if req.ai_model_id:
        ai_model = db.query(AIModel).filter(AIModel.id == req.ai_model_id).first()
        if not ai_model:
            raise HTTPException(status_code=404, detail="AI Model not found")

    # 2. Check for Duplicates
    if db.query(VMInstance).filter(VMInstance.name == req.name).first():
        raise HTTPException(status_code=400, detail="VM name already exists")

    # 3. Create VM Record
    new_vm = VMInstance(
        name=req.name,
        project_id=req.project_id,
        flavor_id=req.flavor_id,
        status="PROVISIONING"
    )
    db.add(new_vm)
    db.commit()
    db.refresh(new_vm)

    # 4. Start Metering (Usage Session)
    usage = VMUsage(
        vm_id=new_vm.id,
        ai_model_id=req.ai_model_id,
        start_time=datetime.now(timezone.utc),
        applied_hw_rate=flavor.hourly_rate,
        applied_model_rate=ai_model.hourly_surcharge if ai_model else 0.0
    )
    db.add(usage)
    db.commit()

    # 5. Launch Infrastructure (Stub or KubeVirt)
    try:
        if k8s:
            # Prod/Dev with KubeVirt
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
            k8s.custom_api.create_namespaced_custom_object("kubevirt.io", "v1", "default", "virtualmachineinstances", vmi_manifest)
        else:
            # Stub Mode (No KubeVirt Client or intentional Stub)
            logger.info("Running in STUB MODE: Skipping actual KubeVirt creation.")
        
        # update status
        new_vm.status = "RUNNING"
        db.commit()
        
    except Exception as e:
        logger.error(f"VM Creation Failed: {e}")
        # Rollback Usage
        db.delete(usage)
        db.delete(new_vm)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))

    return VMStatusResponse(
        id=new_vm.id, name=new_vm.name, status=new_vm.status,
        flavor_name=flavor.name, current_cost=0.0
    )

@router.delete("/{name}")
def delete_vm(name: str, db: Session = Depends(get_db)):
    """Stop VM: Stop Usage -> Calculate Cost -> Terminate Infra"""
    vm = db.query(VMInstance).filter(VMInstance.name == name).first()
    if not vm:
        raise HTTPException(status_code=404, detail="VM not found")
        
    # 1. Stop Metering
    active_usage = db.query(VMUsage).filter(VMUsage.vm_id == vm.id, VMUsage.end_time.is_(None)).first()
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
        
        db.commit()

    # 2. Terminate Infra
    if k8s:
        try:
            k8s.custom_api.delete_namespaced_custom_object("kubevirt.io", "v1", "default", "virtualmachineinstances", name)
        except Exception as e:
            logger.warning(f"KubeVirt delete failed (might be stub): {e}")

    # 3. Update DB
    vm.status = "TERMINATED"
    db.commit()

    return {"status": "success", "message": f"VM {name} terminated. Cost recorded."}

@router.post("/{name}/switch_model")
def switch_model(name: str, req: VMSwitchModelRequest, db: Session = Depends(get_db)):
    """Dynamic Billing: Close current usage -> Start new usage with new rate"""
    vm = db.query(VMInstance).filter(VMInstance.name == name).first()
    if not vm:
        raise HTTPException(status_code=404, detail="VM not found")
        
    new_model = db.query(AIModel).filter(AIModel.id == req.new_model_id).first()
    if not new_model:
        raise HTTPException(status_code=404, detail="Model not found")
        
    # 1. Close active usage
    active_usage = db.query(VMUsage).filter(VMUsage.vm_id == vm.id, VMUsage.end_time.is_(None)).first()
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
    db.commit()
    
    return {"status": "success", "message": f"Switched to model {new_model.name}. Billing rate updated."}
