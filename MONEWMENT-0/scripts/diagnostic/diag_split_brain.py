import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def diagnosis():
    db_url = "postgresql+asyncpg://postgres.vtcwsehwbyzpjuirviir:gmlwkTltkfkdgo123@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
    engine = create_async_engine(db_url, connect_args={"statement_cache_size": 0, "prepared_statement_cache_size": 0})
    
    async with engine.connect() as conn:
        print("--- [SYSTEM DISCREPANCY AUDIT] ---")
        
        # Check assets table (Core's Target)
        try:
            res = await conn.execute(text("SELECT count(*) FROM schema_stratum_vendors.assets;"))
            print(f"Core Target [assets]: {res.scalar()} records")
        except Exception as e:
            print(f"Core Target [assets]: ERROR - {e}")

        # Check raw_archive table (Forager's Target)
        try:
            res = await conn.execute(text("SELECT count(*) FROM schema_stratum_vendors.raw_archive;"))
            print(f"Forager Target [raw_archive]: {res.scalar()} records")
        except Exception as e:
            print(f"Forager Target [raw_archive]: ERROR - {e}")
            
        print("\n--- [PROCESS ALIGNMENT] ---")
        # Check if REX Node IDs exist in any table
        try:
            res = await conn.execute(text("SELECT DISTINCT areum_id FROM schema_stratum_vendors.assets;"))
            areums = [str(row[0]) for row in res if row[0]]
            print(f"Active AREUM IDs in [assets]: {len(areums)}")
        except: pass

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(diagnosis())
