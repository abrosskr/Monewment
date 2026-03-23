import asyncio
from sqlalchemy import text
from core.database import engine

async def resurrect_reci():
    print("Resurrecting recilabel stratum and recilabeler queen...")
    async with engine.begin() as conn:
        # 1. Resurrect Stratum
        await conn.execute(text("""
            UPDATE schema_registry.stratums 
            SET status = 'ACTIVE', 
                last_seen_at = NOW() 
            WHERE stratum_name = 'recilabel'
        """))
        print("Stratum 'recilabel' set to ACTIVE.")
        
        # 2. Resurrect Queen and assign to recilabel and EDENVALE (a8527246-b140-42cf-b304-00f4587ee1f4)
        await conn.execute(text("""
            UPDATE schema_registry.queens 
            SET status = 'ACTIVE', 
                stratum_ids = CAST(ARRAY['604c3454-88c5-4c27-8033-a7f5d548ad2b', 'a8527246-b140-42cf-b304-00f4587ee1f4'] AS uuid[]),
                last_seen_at = NOW() 
            WHERE queen_name = 'recilabeler'
        """))
        print("Queen 'recilabeler' set to ACTIVE and assigned to recilabel and EDENVALE.")

if __name__ == "__main__":
    asyncio.run(resurrect_reci())
