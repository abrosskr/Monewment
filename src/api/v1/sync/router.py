from fastapi import APIRouter, Depends, HTTPException
from typing import Dict
from src.core.security import get_api_key_user
from src.models import User

router = APIRouter()

@router.post("/generate", summary="Generate Synthetic Data", response_model=Dict[str, str])
async def generate_data(
    prompt: str,
    user: User = Depends(get_api_key_user)
):
    """
    [B2B] Request AI synthetic data generation.
    - **prompt**: Text description of data to generate
    - **Header**: X-API-Key required
    """
    # 1. Create Job Request
    import uuid
    from loguru import logger
    from src.core.protocol import JobRequest, JobType
    from src.core.scheduler import Scheduler
    from src.core.socket_manager import SocketManager
    
    job_id = f"job_{uuid.uuid4().hex[:8]}"
    job_req = JobRequest(
        job_id=job_id,
        type=JobType.GEN_TEXT,
        data={"prompt": prompt},
        requirements={"min_vram": 8} # Basic requirement
    )
    
    # 2. Schedule
    scheduler = Scheduler()
    worker_id = await scheduler.schedule_job(job_req)
    
    if not worker_id:
        raise HTTPException(status_code=503, detail="No suitable Ant workers available.")
        
    # 3. Dispatch
    manager = SocketManager.get_instance()
    
    if not manager.get_connection(worker_id):
         raise HTTPException(status_code=503, detail=f"Worker {worker_id} scheduled but connection lost.")
         
    try:
        # Send Job Request to Ant
        import json
        payload = {"type": "job_request", "data": job_req.dict()}
        msg = json.dumps(payload, default=str)
        await manager.send_message(worker_id, msg)
        logger.info(f"🚀 Job {job_id} dispatched to {worker_id}")
        
        return {"status": "assigned", "job_id": job_id, "worker_id": worker_id}
        
    except Exception as e:
        logger.error(f"Dispatch Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to dispatch job to worker.")

@router.get("/tasks/{task_id}", summary="Check Task Status")
async def get_task_status(
    task_id: str,
    user: User = Depends(get_api_key_user)
):
    """
    [B2B] Check status of a generation task.
    """
    return {"task_id": task_id, "status": "processing", "progress": 45}
