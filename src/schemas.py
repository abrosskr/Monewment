from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from src.models import UserRole, RoomStatus

# --- 공통 설정 ---
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True) # ORM 객체를 Pydantic으로 변환 허용

# --- User Schemas ---
class UserCreate(BaseSchema):
    email: EmailStr
    password: str
    organization_name: str # 가입 시 회사 이름 필수

class UserResponse(BaseSchema):
    id: int
    email: EmailStr
    role: UserRole
    org_id: int

# --- Policy Schemas ---
class PolicyCreate(BaseSchema):
    name: str
    rules: Dict[str, Any] # JSON 형식

class PolicyResponse(BaseSchema):
    id: int
    name: str
    rules: Dict[str, Any]

# --- Project Schemas ---
class ProjectCreate(BaseSchema):
    name: str
    description: Optional[str] = None

class ProjectResponse(BaseSchema):
    id: int
    name: str
    description: Optional[str]

# --- Room Schemas ---
class RoomCreate(BaseSchema):
    name: str
    policy_id: Optional[int] = None

class RoomResponse(BaseSchema):
    id: int
    name: str
    status: RoomStatus
    k8s_namespace: Optional[str] = None
    policy: Optional[PolicyResponse] = None

# [Phase 2] API 응답 표준화
class APIResponse(BaseModel):
    """표준 API 응답 형식"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class HealthCheckResponse(BaseModel):
    """Health Check 응답 형식"""
    status: str  # "healthy" or "unhealthy"
    checks: Dict[str, bool]
    timestamp: Optional[str] = None