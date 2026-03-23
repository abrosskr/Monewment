import asyncio
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent
if str(root / "MONEWMENT-0") not in sys.path:
    sys.path.insert(0, str(root / "MONEWMENT-0"))

from sqlalchemy import text
from core.database import engine

async def list_active_entities():
    print("--- [AUDIT] All Queens ---")
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT queen_id, queen_name, status, last_seen_at FROM schema_registry.queens"))
        rows = res.fetchall()
        for r in rows:
            print(f"ID: {r[0]}, Name: {r[1]}, Status: {r[2]}, LastSeen: {r[3]}")

        print("\n--- [AUDIT] Stratum Info ---")
        res = await conn.execute(text("SELECT stratum_id, stratum_name FROM schema_registry.stratums"))
        rows = res.fetchall()
        for r in rows:
            print(f"ID: {r[0]}, Name: {r[1]}")

    print("\n--- [AUDIT] Finished ---")

if __name__ == "__main__":
    asyncio.run(list_active_entities())
