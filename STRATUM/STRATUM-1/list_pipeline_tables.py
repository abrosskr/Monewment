# 🛰️ Imperial Schema Inspector v3
# c:\monewment\STRATUM\STRATUM-1\list_pipeline_tables.py

import asyncio
from sqlalchemy import text
from core.database import AsyncSessionLocal

async def inspect():
    print("[INSPECT] Listing all tables in schema_pipeline...")
    async with AsyncSessionLocal() as db:
        try:
            q = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'schema_pipeline'
            """)
            res = await db.execute(q)
            rows = res.fetchall()
            if not rows:
                print("    [EMPTY] No tables found in schema_pipeline.")
            for row in rows:
                print(f"    - {row[0]}")
        except Exception as e:
            print(f"    [ERROR] {e}")

if __name__ == "__main__":
    asyncio.run(inspect())
