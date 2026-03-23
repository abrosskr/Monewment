
import asyncio
from sqlalchemy import text
from core.database import engine

async def run():
    async with engine.begin() as conn:
        # 1. Backfilling
        await conn.execute(text("UPDATE schema_registry.stratums SET last_seen_at = last_seen_at + INTERVAL '9 hours'"))
        await conn.execute(text("UPDATE schema_registry.ants SET last_seen_at = last_seen_at + INTERVAL '9 hours'"))
        
        # 2. Verification
        res = await conn.execute(text("SELECT last_seen_at FROM schema_registry.stratums LIMIT 5"))
        rows = res.fetchall()
        print(f"DB_VAL_CHECK: {[str(r[0]) for r in rows]}")

if __name__ == "__main__":
    asyncio.run(run())
