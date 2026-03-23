
import asyncio
from sqlalchemy import text
from core.database import engine
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

async def run():
    # [TEMPORAL CONSTITUTION] DB 엔진의 자동 변환을 차단하기 위해 문자열로 주입
    now_str = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
    async with engine.begin() as conn:
        print(f"FORCING STRING-BASED TEMPORAL RESET TO: {now_str}")
        await conn.execute(text("UPDATE schema_registry.stratums SET last_seen_at = :now"), {"now": now_str})
        await conn.execute(text("UPDATE schema_registry.ants SET last_seen_at = :now"), {"now": now_str})
        
        r = await conn.execute(text("SELECT last_seen_at FROM schema_registry.stratums LIMIT 1"))
        print(f"DB_VAL_CHECK: {r.scalar()}")

if __name__ == "__main__":
    asyncio.run(run())
