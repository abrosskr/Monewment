from fastapi import FastAPI, BackgroundTasks
from pathlib import Path
import uuid
import os
import asyncio

# Spawn-Ready Imports
try:
    from schemas import HarvestRequest
    from core.services.scraper_service import run_scraper_logic
except ImportError:
    from .schemas import HarvestRequest
    from .core.services.scraper_service import run_scraper_logic

app = FastAPI(title="OMNI-CRAWLER [BLOOM_FIELD] v1.0")

# Path Configuration (Pathlib for Cross-Platform)
BASE_DIR = Path(__file__).parent
BUFFER_DIR = BASE_DIR / "data" / "buffer"
BUFFER_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/harvest")
async def harvest(request: HarvestRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    
    # [The Switchboard] Direct to Harvest Engine
    background_tasks.add_task(run_scraper_logic, request, task_id, BUFFER_DIR)
    
    return {
        "status": "Accepted",
        "task_id": task_id,
        "mode": "Horizontal_Separation",
        "buffer_path": str(BUFFER_DIR),
        "message": f"Harvesting started for {request.category}. Output will be in local buffer."
    }

async def run_scraper_logic_placeholder(request, task_id, buffer_path):
    # This will be replaced by the actual refined service
    print(f"DEBUG: Task {task_id} started for {request.url}")
    await asyncio.sleep(1)
    print(f"DEBUG: Task {task_id} finished")
