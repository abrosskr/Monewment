import asyncio
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent
if str(root / "MONEWMENT-0") not in sys.path:
    sys.path.insert(0, str(root / "MONEWMENT-0"))

from sqlalchemy import text
from core.database import engine

async def resurrect_core():
    print("--- [RESURRECTION] Core Entities ---")
    async with engine.begin() as conn:
        # 2. Resurrect IMPERIAL_CORE
        # We try both ID and Name to be sure
        res2 = await conn.execute(text("""
            UPDATE schema_registry.monewments
            SET status = 'ACTIVE', died_at = NULL, death_reason = NULL, last_seen_at = NOW(), born_at = NOW()
            WHERE monewment_id = 'd8a9e0a0-0000-0000-0000-000000000000' OR display_name = 'IMPERIAL_CORE'
        """))
        print(f"IMPERIAL_CORE resurrected: {res2.rowcount} row(s)")

        # 3. Resurrect QUEEN-SFIS (Forager Command)
        res3 = await conn.execute(text("""
            UPDATE schema_registry.queens
            SET status = 'ACTIVE', died_at = NULL, death_reason = NULL, last_seen_at = NOW(), born_at = NOW()
            WHERE queen_id = 'e5388cf9-4ce2-400e-8de1-f9e2a5bb18bd'
        """))
        print(f"QUEEN-SFIS resurrected: {res3.rowcount} row(s)")

    print("--- [RESURRECTION] Finished ---")

if __name__ == "__main__":
    asyncio.run(resurrect_core())
