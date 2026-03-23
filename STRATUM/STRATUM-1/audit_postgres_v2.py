import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

LOCAL_POSTGRES_URL = "postgresql+asyncpg://forager:forager@127.0.0.1:5432/forager"

async def check_query(conn, query, label, params=None):
    try:
        res = await conn.execute(text(query), params or {})
        rows = res.fetchall()
        print(f"[OK] {label}: {rows}")
        return rows
    except Exception as e:
        print(f"[FAIL] {label}: {e}")
        return None

async def audit():
    engine = create_async_engine(LOCAL_POSTGRES_URL)
    
    print("--- [AUDIT] PostgreSQL High-Fidelity Infrastructure Check ---")
    
    async with engine.connect() as conn:
        # Check schemas
        await check_query(conn, "SELECT schema_name FROM information_schema.schemata", "Schemas")
        
        # Check tables in stratum-1
        schema = "schema_stratum_stratum_1"
        await check_query(conn, f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}'", f"Tables in {schema}")
        
        # Check counts
        await check_query(conn, f"SELECT COUNT(*) FROM {schema}.assets", "Asset Count")
        await check_query(conn, f"SELECT COUNT(*) FROM {schema}.target_sites", "Target Site Count")
        
        # Check triggers
        await check_query(conn, f"SELECT trigger_name, event_manipulation, event_object_table FROM information_schema.triggers WHERE trigger_schema = '{schema}'", "Triggers")

if __name__ == "__main__":
    try:
        asyncio.run(audit())
    except Exception as e:
        print(f"CRITICAL: Failed to connect or execute audit: {e}")
