import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

LOCAL_POSTGRES_URL = "postgresql+asyncpg://forager:forager@127.0.0.1:5432/forager"

async def sync():
    engine = create_async_engine(LOCAL_POSTGRES_URL)
    async with engine.begin() as conn:
        print("[*] Synchronizing Shadow Data to Canonical Stratum...")
        
        src = "schema_stratum_vendors"
        tgt = "schema_stratum_stratum_1"
        
        tables = ["vendors", "target_sites", "assets"]
        
        for table in tables:
            print(f"  -> Moving {table}...")
            # Use INSERT INTO ... SELECT for maximum fidelity
            # ON CONFLICT DO NOTHING to prevent errors if some data exists
            await conn.execute(text(f"""
                INSERT INTO {tgt}.{table}
                SELECT * FROM {src}.{table}
                ON CONFLICT (id) DO NOTHING
            """))
            
        print("[OK] Synchronization Complete.")

if __name__ == "__main__":
    asyncio.run(sync())
