import asyncio
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent
if str(root / "MONEWMENT-0") not in sys.path:
    sys.path.insert(0, str(root / "MONEWMENT-0"))

from sqlalchemy import text
from core.database import engine

async def diagnose_schema():
    print("--- [DIAGNOSE] Schema Audit ---")
    async with engine.connect() as conn:
        # Registry
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_schema='schema_registry' AND table_name='data_movements'"))
        cols = [r[0] for r in res.fetchall()]
        print(f"schema_registry.data_movements columns: {cols}")
        
        # Stratum (just one)
        res = await conn.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'schema_stratum_%' LIMIT 1"))
        stratum = res.scalar()
        if stratum:
            res = await conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_schema='{stratum}' AND table_name='assets' AND column_name='rex_summary'"))
            print(f"{stratum}.assets has rex_summary: {res.fetchone() is not None}")
        
    print("--- [DIAGNOSE] Audit Finished ---")

if __name__ == "__main__":
    asyncio.run(diagnose_schema())
