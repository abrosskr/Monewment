
import asyncio
from sqlalchemy import text
from core.database import engine
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

async def run():
    now_str = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
    async with engine.begin() as conn:
        print(f"FORCING RAW SQL TEMPORAL RESET TO: {now_str}")
        # 바인딩 변수 대신 문자열을 쿼리에 직접 주입하여 드라이버 보정 회피
        await conn.execute(text(f"UPDATE schema_registry.stratums SET last_seen_at = '{now_str}'"))
        await conn.execute(text(f"UPDATE schema_registry.ants SET last_seen_at = '{now_str}'"))
        
        r = await conn.execute(text("SELECT last_seen_at FROM schema_registry.stratums LIMIT 1"))
        print(f"DB_VAL_CHECK: {r.scalar()}")

if __name__ == "__main__":
    asyncio.run(run())
