from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid

class JobType(str, Enum):
    TEXT_TO_IMAGE = "TEXT_TO_IMAGE"
    IMAGE_TO_IMAGE = "IMAGE_TO_IMAGE"
    TEXT_GENERATION = "TEXT_GENERATION"
    VIDEO_RENDERING = "VIDEO_RENDERING"
    RENDER_3D = "RENDER_3D" # [Phase 6-6] New Type

class JobStatus(str, Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class JobRequest(BaseModel):
    """
    User -> Queen -> Ant
    """
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: int
    job_type: JobType
    params: Dict[str, Any] # e.g. {"prompt": "cyberpunk city", "steps": 50}
    
    requirements: Dict[str, Any] = Field(default={}) 
    # e.g. {"min_vram": 16, "model_name": "stable-diffusion-xl"}
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None

class JobResult(BaseModel):
    """
    Ant -> Queen -> User (via API/DB)
    """
    job_id: str
    status: JobStatus
    worker_id: str # Ant Client ID
    
    output_urls: List[str] = [] # S3 or Signed URLs
    output_data: Dict[str, Any] = {} # [Phase 6-6] Flexible Output Data
    execution_time_ms: int = 0
    
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
