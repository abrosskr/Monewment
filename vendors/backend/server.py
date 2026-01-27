import asyncio
import logging
import uvicorn
import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from app.core.pipeline import PipelineService
from app.api.v1 import intelligence
from app.database import engine, Base, SessionLocal
from app.services.taste_service import TasteAssetService
from app.core.fis_generator import FISGenerator
from app.models.fis import FISProfile

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SentientServer")

# Global Singleton
pipeline: Optional[PipelineService] = None

# --- Pydantic Models for API ---
class ControlCommand(BaseModel):
    mode: Optional[str] = None # AUTO, MANUAL, CALIBRATION
    manual_watts: Optional[float] = None

class RecordCommand(BaseModel):
    action: str # START, STOP
    metadata: Optional[Dict[str, Any]] = {}

# --- WebSocket Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"WS Send fail: {e}")
                
manager = ConnectionManager()

# --- Background Broadcaster ---
async def state_broadcaster():
    """Pushes Pipeline State to WS Clients at 10Hz"""
    while True:
        if pipeline and pipeline.is_running:
            state = pipeline.get_current_state()
            if state:
                await manager.broadcast(state)
        await asyncio.sleep(0.1)

# --- Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global pipeline
    logger.info("🚀 Starting Sentient Control Server...")
    
    # Initialize Asset Tables
    logger.info("📦 Synchronizing Asset Database...")
    Base.metadata.create_all(bind=engine)
    
    pipeline = PipelineService()
    await pipeline.start()
    
    # Start Broadcaster
    asyncio.create_task(state_broadcaster())
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Sentient Control Server...")
    if pipeline:
        await pipeline.stop()
    logger.info("✅ Server Stopped.")

app = FastAPI(lifespan=lifespan, title="Sentient Kitchen Server")

# --- REST Endpoints ---

@app.get("/state")
async def get_state():
    if not pipeline: raise HTTPException(503, "Pipeline not ready")
    return pipeline.get_current_state()

@app.post("/control")
async def control_pipeline(cmd: ControlCommand):
    if not pipeline: raise HTTPException(503, "Pipeline not ready")
    
    if cmd.mode:
        pipeline.set_mode(cmd.mode)
    
    if cmd.manual_watts is not None:
        pipeline.set_manual_command(cmd.manual_watts)
        
    return {"status": "accepted", "mode": pipeline.mode, "manual_watts": pipeline.manual_watts}

@app.post("/record")
async def manage_recorder(cmd: RecordCommand):
    if not pipeline: raise HTTPException(503, "Pipeline not ready")
    
    if cmd.action == "START":
        sid = pipeline.start_recording(cmd.metadata)
        return {"status": "started", "session_id": sid}
    elif cmd.action == "STOP":
        pipeline.stop_recording()
        return {"status": "stopped"}
    else:
        raise HTTPException(400, "Invalid action")

@app.post("/calibration/trigger")
async def trigger_calibration():
    if not pipeline: raise HTTPException(503, "Pipeline not ready")
    asyncio.create_task(pipeline.run_calibration_sequence())
    return {"status": "triggered"}

@app.post("/taste/ingest")
async def ingest_taste(session_id: str, scores: Dict[str, float], cluster: str = "GENERIC"):
    """Layer C: Ingest Human Evaluation"""
    success = TasteAssetService.ingest_evaluation(session_id, scores, cluster)
    if not success: raise HTTPException(500, "Ingestion Failed")
    return {"status": "success"}

@app.post("/fis/synthesize")
async def synthesize_fis(source_id: int, session_id: Optional[str] = None):
    """Refinery Step 5: Fusion Product Synthesis"""
    db = SessionLocal()
    try:
        product = FISGenerator.synthesize_from_source(db, source_id, session_id)
        if not product: raise HTTPException(404, "Source not found")
        return product.model_dump()
    finally:
        db.close()

@app.post("/fis/load")
async def load_fis(profile: FISProfile):
    if not pipeline: raise HTTPException(503, "Pipeline not ready")
    pipeline.load_fis_profile(profile)
    return {"status": "loaded", "target": profile.name}

# X-Intelligence Router Registration
app.include_router(intelligence.router, prefix="/api/v1/intel", tags=["X-Intelligence"])

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    # Fix import path for uvicorn when running as script
    sys.path.append(os.getcwd())
    uvicorn.run(app, host="0.0.0.0", port=8000)
