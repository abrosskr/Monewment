# 🛰️ Imperial Stratum Inspector
# c:\monewment\STRATUM\STRATUM-1\list_stratums.py

import asyncio
from sqlalchemy import text
from core.database import AsyncSessionLocal

async def inspect():
    print("[INSPECT] Listing Stratums in schema_registry.stratums...")
    async with AsyncSessionLocal() as db:
        try:
            q = text("SELECT stratum_id::text, stratum_name, status FROM schema_registry.stratums")
            res = await db.execute(q)
            rows = res.fetchall()
            if not rows:
                print("    [EMPTY] No stratums found.")
            for row in rows:
                print(f"    - ID: {row[0]} | Name: {row[1]} | Status: {row[2]}")
        except Exception as e:
            print(f"    [ERROR] {e}")

if __name__ == "__main__":
    asyncio.run(inspect())
