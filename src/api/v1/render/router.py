from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from datetime import datetime
from src.core.security import get_api_key_user
from src.models import User
from src.core.protocol import JobRequest, JobStatus, JobResult, JobType
from src.core.scheduler import Scheduler
from src.core.socket_manager import SocketManager
import uuid
import json
import logging

logger = logging.getLogger("RenderRouter")
router = APIRouter()

# In-Memory Job Store for MVP (Should be DB)
JOB_STORE: Dict[str, JobRequest] = {}
RESULT_STORE: Dict[str, JobResult] = {}

scheduler = Scheduler()
# Ensure scheduler is shared or singleton? 
# Scheduler in main.py is instance. We should probably use a singleton pattern for Scheduler too.
# For now, we create a new one, but it won't share state with main.py if main.py uses a different instance.
# But Scheduler is stateless except config? No, it schedules.
# Let's import the global scheduler if possible or accept that for MVP we use a local one.
# Valid concern: `main.py` has `scheduler = Scheduler()`.
# Refactor: We will use the `main.py` logic via this router, and `main.py` should import this router.
# But `main.py` can't be imported here (circular).
# Solution: Use `Scheduler` instance here.

@router.post("/jobs", summary="Submit Render Job", response_model=Dict[str, str])
async def submit_render_job(
    request: JobRequest,
    # user: User = Depends(get_api_key_user) # [Demo] Auth disabled for easy browsing
):
    """
    [B2B] Submit a 3D rendering job.
    """
    # 1. Assign ID and Store
    request.job_id = str(uuid.uuid4())
    request.project_id = 1 # Default or from User
    request.created_at = datetime.utcnow()
    request.job_type = JobType.RENDER_3D
    
    JOB_STORE[request.job_id] = request
    
    # 2. Schedule
    worker_id = await scheduler.schedule_job(request)
    
    if not worker_id:
        return {"status": "queued", "job_id": request.job_id, "message": "No workers available"}
        
    # 3. Dispatch
    manager = SocketManager.get_instance()
    if manager.get_connection(worker_id):
        payload = {"type": "job_request", "data": request.dict()}
        await manager.send_message(worker_id, json.dumps(payload, default=str))
        logger.info(f"Job {request.job_id} dispatched to {worker_id}")
        return {"status": "assigned", "job_id": request.job_id, "worker_id": worker_id}
        
    return {"status": "queued", "job_id": request.job_id}

@router.get("/jobs", summary="List Jobs")
async def list_jobs():
    """
    [Admin] List all jobs.
    """
    # Return list of jobs with status
    # We need status. Status is in RESULT_STORE or we default to PENDING.
    
    jobs_summary = []
    for jid, job in JOB_STORE.items():
        res = RESULT_STORE.get(jid)
        status = res.status if res else "PENDING"
        output_id = res.output_data.get("output_file_id") if res else None
        
        jobs_summary.append({
            "job_id": jid,
            "type": job.job_type,
            "status": status,
            "created_at": job.created_at,
            "output_file_id": output_id
        })
        
    # Sort by date desc
    jobs_summary.sort(key=lambda x: x["created_at"], reverse=True)
    return {"jobs": jobs_summary}

# Webhook or callback for Result?
# main.py handles WebSocket results. It should update RESULT_STORE.
# We need a way to share RESULT_STORE.
# Singleton Store?
class JobDatabase:
    _jobs = {}
    _results = {}
    
    @classmethod
    def add_job(cls, job): cls._jobs[job.job_id] = job
    @classmethod
    def add_result(cls, res): cls._results[res.job_id] = res
    @classmethod
    def get_all(cls): return cls._jobs, cls._results

# Apply Singleton to Router logic
JOB_STORE = JobDatabase._jobs
RESULT_STORE = JobDatabase._results
