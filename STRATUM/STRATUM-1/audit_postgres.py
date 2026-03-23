import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Using the URL from config.py
LOCAL_POSTGRES_URL = "postgresql+asyncpg://forager:forager@127.0.0.1:5432/forager"

async def audit():
    engine = create_async_engine(LOCAL_POSTGRES_URL)
    async with engine.connect() as conn:
        print("--- [AUDIT] PostgreSQL Infrastructure Check ---")
        
        # 1. Verify schema schemas
        res = await conn.execute(text("SELECT schema_name FROM information_schema.schemata"))
        schemas = [r[0] for r in res.fetchall()]
        print(f"Schemas Found: {schemas}")
        
        # 2. Check counts in schema_stratum_stratum_1
        # (Assuming the schema prefix is used as per STRATUM-1 logic)
        schema = "schema_stratum_stratum_1"
        
        try:
            res = await conn.execute(text(f"SELECT COUNT(*) FROM {schema}.assets"))
            asset_count = res.scalar()
            print(f"Asset Count ({schema}.assets): {asset_count}")
            
            res = await conn.execute(text(f"SELECT COUNT(*) FROM {schema}.targets"))
            target_count = res.scalar()
            print(f"Target Count ({schema}.targets): {target_count}")
            
        except Exception as e:
            print(f"Error checking {schema}: {e}")

        # 3. Check for triggers
        res = await conn.execute(text("""
            SELECT trigger_name 
            FROM information_schema.triggers 
            WHERE trigger_schema = :schema
        """), {"schema": schema})
        triggers = [r[0] for r in res.fetchall()]
        print(f"Triggers in {schema}: {triggers}")

if __name__ == "__main__":
    asyncio.run(audit())
