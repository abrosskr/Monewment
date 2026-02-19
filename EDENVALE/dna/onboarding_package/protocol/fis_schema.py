from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class RegisterRequest(BaseModel):
    instance_id: str
    instance_key: str
    layer: str
    version: str = "4.0.0"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RegisterResponse(BaseModel):
    status: str
    access_token: str
    master_id: str = "EDENVALE"
    expires_at: datetime

class HeartbeatMessage(BaseModel):
    instance_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    cpu_usage: float
    memory_usage: float
    status: str = "HEALTHY"
