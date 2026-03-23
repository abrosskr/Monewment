import asyncio
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent
if str(root / "MONEWMENT-0") not in sys.path:
    sys.path.insert(0, str(root / "MONEWMENT-0"))

from sqlalchemy import text
from core.database import engine

async def get_stratum_queen():
    target_stratum = "badd8a15-5e63-4d24-81fd-489e8973cb85"
    print(f"--- [LOOKUP] Queen for Stratum {target_stratum} ---")
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT stratum_id, stratum_name, queen_id FROM schema_registry.stratums WHERE stratum_id = :sid"), {"sid": target_stratum})
        row = res.fetchone()
        if row:
            print(f"Stratum: {row.stratum_name} ({row.stratum_id}), QueenID: {row.queen_id}")
        else:
            print("Stratum not found by ID. Checking by name 'stratum_1'...")
            res = await conn.execute(text("SELECT stratum_id, stratum_name, queen_id FROM schema_registry.stratums WHERE stratum_name = 'stratum_1'"))
            row = res.fetchone()
            if row:
                print(f"Stratum: {row.stratum_name} ({row.stratum_id}), QueenID: {row.queen_id}")

    print("\n--- [LOOKUP] Finished ---")

if __name__ == "__main__":
    asyncio.run(get_stratum_queen())
