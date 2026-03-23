# 🛠️ Imperial Alignment — Registry vs Physics
# c:\monewment\STRATUM\STRATUM-1\align_registry.py

import asyncio
from sqlalchemy import text
from core.database import AsyncSessionLocal

async def align():
    print("[ALIGN] Aligning Registry Stratum Name to 'stratum_1'...")
    async with AsyncSessionLocal() as db:
        try:
            # Match the existing physical schema name
            q = text("UPDATE schema_registry.stratums SET stratum_name = 'stratum_1' WHERE stratum_id = '3bb565af-e01a-49b8-af27-049e6a642f2d'")
            await db.execute(q)
            await db.commit()
            print("[SUCCESS] Registry Aligned. Pipeline route should now resolve to schema_stratum_stratum_1.")
        except Exception as e:
            print(f"[ERROR] {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(align())
