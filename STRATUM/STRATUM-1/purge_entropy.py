import asyncio
from sqlalchemy import text
from core.database import engine

GOLDEN_QUEEN_ID = 'ba537759-f607-4eda-841c-eeba65a5147b'

async def ultimate_purge():
    async with engine.begin() as conn:
        print("=== [PURGE] 제국 궁극의 정화 개시 (Zero-Entropy Mode) ===")
        
        # 1. Ants(Workers) 완전 삭제 (무조건 전부 비움)
        res_ant = await conn.execute(text("DELETE FROM schema_registry.ants"))
        print(f"  - Ants 테이블 초기화 완료: {res_ant.rowcount} 건 삭제")

        # 2. Areums 완전 삭제
        res_a = await conn.execute(text("DELETE FROM schema_registry.areums"))
        print(f"  - Areums 테이블 초기화 완료: {res_a.rowcount} 건 삭제")

        # 3. Queens 정화 (Golden ID 가 아닌 모든 IN-X 와 DEAD 레코드 삭제)
        q_purge_queens = text("""
            DELETE FROM schema_registry.queens 
            WHERE status = 'DEAD' 
               OR (queen_name LIKE 'QUEEN-IN-%' AND queen_id != :golden_id)
        """)
        res_q = await conn.execute(q_purge_queens, {"golden_id": GOLDEN_QUEEN_ID})
        print(f"  - Queens 정화 완료: {res_q.rowcount} 건 삭제")
        
        print("=== [DONE] 시스템 정화 완료 ===")

if __name__ == "__main__":
    asyncio.run(ultimate_purge())
