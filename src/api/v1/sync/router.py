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
    # TODO: Connect to Scheduler
    job_id = "job_mock_" + prompt[:5]
    return {"status": "queued", "job_id": job_id}

@router.get("/tasks/{task_id}", summary="Check Task Status")
async def get_task_status(
    task_id: str,
    user: User = Depends(get_api_key_user)
):
    """
    [B2B] Check status of a generation task.
    """
    return {"task_id": task_id, "status": "processing", "progress": 45}
