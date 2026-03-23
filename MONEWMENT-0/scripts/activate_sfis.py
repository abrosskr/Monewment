import asyncio
from sqlalchemy import text
from core.database import engine

async def activate_and_employ():
    async with engine.begin() as conn:
        # 1. Activate Stratum
        await conn.execute(text("UPDATE schema_registry.stratums SET status = 'ACTIVE' WHERE stratum_name = 'sfis'"))
        
        # Get Stratum IDs
        res_sfis = await conn.execute(text("SELECT stratum_id FROM schema_registry.stratums WHERE stratum_name = 'sfis'"))
        sfis_id = res_sfis.scalar()
        
        res_eden = await conn.execute(text("SELECT stratum_id FROM schema_registry.stratums WHERE stratum_name = 'vendors' OR stratum_id::text = 'a8527246-b140-42cf-b304-00f4587ee1f4' LIMIT 1"))
        eden_id = res_eden.scalar()
        
        # 2. Register Queen sfis-0
        # Check if already exists first
        res_q = await conn.execute(text("SELECT queen_id FROM schema_registry.queens WHERE queen_name = 'sfis-0'"))
        if not res_q.fetchone():
            await conn.execute(text("""
                INSERT INTO schema_registry.queens (queen_name, queen_type, relationship_type, stratum_ids, status, host_ip)
                VALUES ('sfis-0', 'GENERAL', 'INTERNAL', :s_ids, 'ACTIVE', '127.0.0.1')
            """), {"s_ids": [sfis_id, eden_id]})
            print("Queen sfis-0 registered and employed in EDENVALE.")
        else:
            print("Queen sfis-0 already exists.")
            
if __name__ == "__main__":
    asyncio.run(activate_and_employ())
