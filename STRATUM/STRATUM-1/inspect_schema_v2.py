# 🛰️ Imperial Schema Inspector v2
# c:\monewment\STRATUM\STRATUM-1\inspect_schema_v2.py

import asyncio
from sqlalchemy import text
from core.database import AsyncSessionLocal

async def inspect():
    print("[INSPECT] Checking schema_pipeline.intelligence_reports...")
    async with AsyncSessionLocal() as db:
        try:
            q = text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'schema_pipeline' 
                AND table_name = 'intelligence_reports'
            """)
            res = await db.execute(q)
            rows = res.fetchall()
            if not rows:
                print("    [EMPTY] Table not found or no columns.")
            for row in rows:
                print(f"    - {row[0]} ({row[1]})")
        except Exception as e:
            print(f"    [ERROR] {e}")

if __name__ == "__main__":
    asyncio.run(inspect())
