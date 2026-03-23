
import asyncio
from sqlalchemy import text
from core.database import engine
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

async def run():
    now_kst_naive = datetime.now(KST).replace(tzinfo=None)
    async with engine.begin() as conn:
        print(f"FORCING TEMPORAL RESET TO: {now_kst_naive}")
        await conn.execute(text("UPDATE schema_registry.stratums SET last_seen_at = :now"), {"now": now_kst_naive})
        await conn.execute(text("UPDATE schema_registry.ants SET last_seen_at = :now"), {"now": now_kst_naive})
        
        r = await conn.execute(text("SELECT last_seen_at FROM schema_registry.stratums LIMIT 1"))
        print(f"DB_VAL_CHECK: {r.scalar()}")

if __name__ == "__main__":
    asyncio.run(run())
