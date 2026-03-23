from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class MemberCreate(BaseModel):
    username: str
    email: Optional[str] = None         # 신규 추가: 이메일
    phone_number: Optional[str] = None  # 신규 추가: 전화번호

class MemberResponse(BaseModel):
    id: UUID
    username: str
    email: Optional[str] = None         # 신규 추가
    phone_number: Optional[str] = None  # 신규 추가
    created_at: datetime

    class Config:
        from_attributes = True