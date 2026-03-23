import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

LOCAL_POSTGRES_URL = "postgresql+asyncpg://forager:forager@127.0.0.1:5432/forager"

async def check():
    engine = create_async_engine(LOCAL_POSTGRES_URL)
    async with engine.connect() as conn:
        print("--- [DEEP AUDIT] Constraint & ID Check ---")
        
        # 1. Stratum Check
        res = await conn.execute(text("SELECT stratum_id, stratum_name FROM schema_registry.stratums"))
        stratums = res.fetchall()
        print(f"Registered Stratums: {stratums}")
        
        # 2. Queen Check
        res = await conn.execute(text("SELECT queen_id, queen_name FROM schema_registry.queens"))
        queens = res.fetchall()
        print(f"Registered Queens: {queens}")
        
        # 3. schema_registry.ants schema
        res = await conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'schema_registry' AND table_name = 'ants'
        """))
        print(f"Ants Schema: {res.fetchall()}")
        
        # 4. Check sequences
        res = await conn.execute(text("SELECT * FROM schema_registry.sequences"))
        print(f"Sequences: {res.fetchall()}")

if __name__ == "__main__":
    asyncio.run(check())
