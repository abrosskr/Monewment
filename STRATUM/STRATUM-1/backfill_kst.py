import asyncio
from sqlalchemy import text
from core.database import engine

async def run_backfill():
    async with engine.connect() as conn:
        print("Commencing Temporal Backfill (UTC -> KST)...")
        await conn.execute(text("UPDATE schema_registry.stratums SET last_seen_at = last_seen_at + INTERVAL '9 hours'"))
        await conn.execute(text("UPDATE schema_registry.ants SET last_seen_at = last_seen_at + INTERVAL '9 hours'"))
        await conn.commit()
        print("SUCCESS: 9 Hours Backfilled for all stratums and ants.")

if __name__ == "__main__":
    asyncio.run(run_backfill())
