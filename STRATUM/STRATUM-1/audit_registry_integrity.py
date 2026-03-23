# 🕵️ Imperial Registry Auditor
# c:\monewment\STRATUM\STRATUM-1\audit_registry_integrity.py

import asyncio
from sqlalchemy import text
from core.database import AsyncSessionLocal

async def audit():
    print("[AUDIT] Checking Registry Integrity...")
    async with AsyncSessionLocal() as db:
        # 1. Check AREUMS
        print("\n--- schema_registry.areums ---")
        q = text("SELECT areum_id::text, areum_name, status, last_seen_at FROM schema_registry.areums")
        res = await db.execute(q)
        for row in res.fetchall():
            print(f"  - ID: {row[0]} | Name: {row[1]} | Status: {row[2]} | Last Seen: {row[3]}")

        # 2. Check ANTS (for PHYSICS)
        print("\n--- schema_registry.ants ---")
        q = text("SELECT ant_id::text, ant_name, status, last_seen_at FROM schema_registry.ants")
        res = await db.execute(q)
        for row in res.fetchall():
            print(f"  - ID: {row[0]} | Name: {row[1]} | Status: {row[2]} | Last Seen: {row[3]}")

        # 3. Check QUEENS (for REX)
        print("\n--- schema_registry.queens ---")
        q = text("SELECT queen_id::text, queen_name, status, last_seen_at FROM schema_registry.queens")
        res = await db.execute(q)
        for row in res.fetchall():
            print(f"  - ID: {row[0]} | Name: {row[1]} | Status: {row[2]} | Last Seen: {row[3]}")

        # 4. Check Pipeline AREUM Registry
        print("\n--- schema_pipeline.areum_registry ---")
        q = text("SELECT areum_id::text, areum_name FROM schema_pipeline.areum_registry")
        res = await db.execute(q)
        for row in res.fetchall():
            print(f"  - ID: {row[0]} | Name: {row[1]}")

if __name__ == "__main__":
    asyncio.run(audit())
