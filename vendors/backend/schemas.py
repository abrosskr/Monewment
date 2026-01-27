from pydantic import BaseModel
from typing import Dict, Any, Optional

class TaskInput(BaseModel):
    """
    User input schema.
    """
    key: str
    value: int

class TaskResponse(BaseModel):
    """
    Immediate acknowledgement schema.
    """
    task_id: str
    status: str
    message: str

class TaskStatus(BaseModel):
    """
    Status check schema.
    (Input data is excluded for security)
    """
    task_id: str
    status: str
    result_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
