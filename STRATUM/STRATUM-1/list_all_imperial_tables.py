# 🛰️ Imperial Schema Inspector v5
# c:\monewment\STRATUM\STRATUM-1\list_all_imperial_tables.py

import asyncio
from sqlalchemy import text
from core.database import AsyncSessionLocal

async def inspect():
    print("[INSPECT] Listing all tables in all schema_* namespaces...")
    async with AsyncSessionLocal() as db:
        try:
            q = text("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_schema LIKE 'schema_%' 
                ORDER BY table_schema, table_name
            """)
            res = await db.execute(q)
            rows = res.fetchall()
            current_schema = ""
            for row in rows:
                if row[0] != current_schema:
                    current_schema = row[0]
                    print(f"\n[{current_schema}]")
                print(f"    - {row[1]}")
        except Exception as e:
            print(f"    [ERROR] {e}")

if __name__ == "__main__":
    asyncio.run(inspect())
