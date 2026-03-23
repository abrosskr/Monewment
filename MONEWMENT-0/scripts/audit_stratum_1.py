import asyncio
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent
if str(root / "MONEWMENT-0") not in sys.path:
    sys.path.insert(0, str(root / "MONEWMENT-0"))

from sqlalchemy import text
from core.database import engine

async def audit_stratum_1():
    print("--- [AUDIT] Stratum-1 Assets ---")
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_schema='schema_stratum_stratum_1' AND table_name='assets'"))
        cols = [r[0] for r in res.fetchall()]
        print(f"Columns: {cols}")
        
        # Check if they actually exist
        has_ai = 'ai_summary' in cols
        has_rex = 'rex_summary' in cols
        print(f"Has ai_summary: {has_ai}")
        print(f"Has rex_summary: {has_rex}")
        
    print("--- [AUDIT] Finished ---")

if __name__ == "__main__":
    asyncio.run(audit_stratum_1())
