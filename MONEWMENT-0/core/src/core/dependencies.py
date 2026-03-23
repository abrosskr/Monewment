from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.core.database import async_session_factory
from src.core.context import get_tenant_id

async def get_tenant_db():
    """
    Runtime Isolation Engine (The Switchboard)
    [최적화 포인트]
    1. SET LOCAL 도입: 트랜잭션 종료 시 신분(Role)과 경로(Path)를 즉시 postgres로 복구.
    2. Explicit Transaction: session.begin()을 통해 LOCAL 명령의 효력을 보장.
    3. Membership Grant: 관리자가 테넌트 Role로 변신할 수 있는 권한을 매번 확인.
    """
    queen_id = get_tenant_id()
    if not queen_id:
        raise HTTPException(status_code=400, detail="Tenant ID missing in request context")

    async with async_session_factory() as session:
        # 1. 명시적 트랜잭션 시작 (SET LOCAL은 트랜잭션 안에서만 유효)
        async with session.begin():
            try:
                # 2. 신분 상승 권한 부여 (이미 부여되어 있어도 안전함)
                await session.execute(text(f"GRANT role_{queen_id} TO postgres"))
                
                # 3. 테넌트 전용 방으로 경로 고정 (트랜잭션 종료 시 자동 RESET)
                await session.execute(text(f"SET LOCAL search_path TO queen_{queen_id}"))
                
                # 4. 테넌트 전용 권한으로 강등 (트랜잭션 종료 시 자동 RESET)
                # 이 시점부터 session은 본인 방 외에는 볼 수도, 만질 수도 없습니다.
                await session.execute(text(f"SET LOCAL ROLE role_{queen_id}"))
                
                yield session
                
            except Exception as e:
                # 에러 발생 시 즉시 롤백하여 세션 오염 방지
                await session.rollback()
                raise HTTPException(status_code=500, detail=f"Database Isolation Error: {str(e)}")
            # [자동] async with session.begin()이 끝날 때 COMMIT/ROLLBACK과 함께 ROLE이 RESET됩니다.