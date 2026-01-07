import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch
from src.core.protocol import JobRequest, JobType
from src.core.scheduler import Scheduler, AntNodeInfo
from datetime import datetime

# We can't easily spin up full FastAPI + WebSocket in a unit test without TestClient and extensive mocking.
# Instead, we will test the logic flow: Scheduler -> Logic -> Mock Dispatch

@pytest.mark.asyncio
async def test_scheduler_logic():
    scheduler = Scheduler()
    
    # Mock Redis return
    mock_ant = AntNodeInfo(
        client_id="ant-1",
        gpu_model="RTX_4090",
        status="ONLINE",
        last_seen=datetime.utcnow()
    )
    
    with patch.object(scheduler, '_get_online_ants', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [mock_ant]
        
        req = JobRequest(
            project_id=1,
            job_type=JobType.TEXT_TO_IMAGE,
            params={"prompt": "test"},
            requirements={"min_vram": 16}
        )
        
        worker_id = await scheduler.schedule_job(req)
        assert worker_id == "ant-1"

@pytest.mark.asyncio
async def test_scheduler_no_match():
    scheduler = Scheduler()
    with patch.object(scheduler, '_get_online_ants', new_callable=AsyncMock) as mock_get:
        # Ant has weak GPU
        mock_get.return_value = [
            AntNodeInfo("ant-small", "RTX_3060", "ONLINE", datetime.utcnow())
        ]
        
        req = JobRequest(
            project_id=1,
            job_type=JobType.TEXT_TO_IMAGE,
            params={"prompt": "test"},
            requirements={"min_vram": 24} # 3060 has 12GB, fail
        )
        
        worker_id = await scheduler.schedule_job(req)
        assert worker_id is None
