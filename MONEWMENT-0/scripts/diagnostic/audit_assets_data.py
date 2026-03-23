import asyncio
import json
import os
import sys

# Ensure MONEWMENT-0 is in path
sys.path.append(os.path.join(os.getcwd(), "MONEWMENT-0"))

from core.database import engine
from sqlalchemy import text

async def audit_assets():
    print("[AUDIT] Checking asset states...")
    try:
        async with engine.connect() as conn:
            res = await conn.execute(text("SELECT id, pipeline_state FROM schema_stratum_vendors.assets"))
            for row in res.fetchall():
                print(f"Asset {row[0]}: {row[1]}")
            
            print("\n[AUDIT] Checking rex_extraction columns...")
            res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_schema = 'schema_stratum_vendors' AND table_name = 'rex_extraction'"))
            for row in res.fetchall():
                print(f"COLUMN: {row[0]}")
            
            print("\n[AUDIT] Checking rex_extraction data...")
            res = await conn.execute(text("SELECT * FROM schema_stratum_vendors.rex_extraction"))
            rows = res.fetchall()
            if not rows:
                print("No extractions found.")
            for row in rows:
                print(f"Extraction for Asset {row[1]}: Confidence={row[6]}")
    finally:
        await engine.dispose()

async def clear_assets():
    print("[MIGRATE] Clearing schema_stratum_vendors.assets...")
    async with engine.begin() as conn:
        await conn.execute(text("DELETE FROM schema_stratum_vendors.assets"))
        print("[OK] Assets cleared.")

if __name__ == "__main__":
    asyncio.run(audit_assets())
