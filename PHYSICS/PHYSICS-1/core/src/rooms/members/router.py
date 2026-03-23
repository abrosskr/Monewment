from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.core.dependencies import get_tenant_db
from .schemas import MemberCreate, MemberResponse

router = APIRouter(prefix="/api/members", tags=["Members"])

@router.post("", response_model=MemberResponse)
async def create_member(
    data: MemberCreate, 
    db: AsyncSession = Depends(get_tenant_db),
    x_queen_id: str = Header(..., alias="X-Queen-ID")
):
    """현재 테넌트의 격리된 방에 새 필드(Email, Phone)를 포함하여 멤버를 등록합니다."""
    try:
        # [수정] 쿼리에 email과 phone_number 필드 추가
        query = text("""
            INSERT INTO members (username, email, phone_number) 
            VALUES (:username, :email, :phone_number) 
            RETURNING id, username, email, phone_number, created_at
        """)
        
        result = await db.execute(query, {
            "username": data.username,
            "email": data.email,
            "phone_number": data.phone_number
        })
        await db.commit() 
        return result.fetchone()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=dict)
async def list_members(
    db: AsyncSession = Depends(get_tenant_db),
    x_queen_id: str = Header(..., alias="X-Queen-ID")
):
    """현재 테넌트의 격리된 방에서 모든 필드를 포함하여 멤버 목록을 조회합니다."""
    # [수정] SELECT 절에 새 필드 추가
    result = await db.execute(text("SELECT id, username, email, phone_number, created_at FROM members"))
    members = [dict(row._mapping) for row in result]
    return {"members": members}