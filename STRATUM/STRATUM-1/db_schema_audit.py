import asyncio, sys, os
from sqlalchemy import text

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.database import engine

async def db_schema_audit():
    try:
        async with engine.connect() as conn:
            q = text("""
                SELECT table_schema, table_name, column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'schema_babel' 
                ORDER BY table_name;
            """)
            res = await conn.execute(q)
            print("=== [DB SCHEMA 실측] ===")
            for r in res.fetchall():
                print(f" - {r[0]}.{r[1]} -> {r[2]} ({r[3]})")
    except Exception as e:
        print(f"[CRITICAL] DB audit failed: {e}")

if __name__ == "__main__":
    asyncio.run(db_schema_audit())
