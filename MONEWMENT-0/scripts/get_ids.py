import asyncio
from sqlalchemy import text
from core.database import engine

async def get_ids():
    async with engine.connect() as conn:
        res_m = await conn.execute(text("SELECT monewment_id FROM schema_registry.monewments LIMIT 1"))
        mon_id = res_m.scalar()
        
        res_s = await conn.execute(text("SELECT stratum_id, stratum_name FROM schema_registry.stratums"))
        rows = res_s.fetchall()
        
        print(f"MON_ID: {mon_id}")
        for r in rows:
            print(f"STRATUM: {r.stratum_name} ({r.stratum_id})")

if __name__ == "__main__":
    asyncio.run(get_ids())
