import asyncio
import sys
from pathlib import Path
from sqlalchemy import text

sys.path.append(str(Path(__file__).resolve().parent.parent))
from core.database import engine

async def full_map_audit():
    print("--- [DEEP MAP AUDIT] Registry to Physical Alignment ---")
    
    async with engine.connect() as conn:
        # 1. List all schemas starting with schema_stratum_
        print("\n[1] Physical Schemas discovered:")
        res = await conn.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'schema_stratum_%'"))
        physical_schemas = [r[0] for r in res.fetchall()]
        for ps in physical_schemas:
            print(f"  - {ps}")

        # 2. List all registered stratums
        print("\n[2] Registry Records (schema_registry.stratums):")
        res = await conn.execute(text("SELECT stratum_id, stratum_name, status FROM schema_registry.stratums"))
        reg_records = res.fetchall()
        for r in reg_records:
            expected_schema = f"schema_stratum_{r.stratum_name}"
            status = "BOUND" if expected_schema in physical_schemas else "GHOST (No Physical Schema)"
            print(f"  - ID: {r.stratum_id} | Name: {r.stratum_name} | Status: {r.status} | Correlation: {status}")

        # 3. Check for specific missing columns in ALL BOUND schemas
        print("\n[3] Deep Column Audit (Expected: rex_processed_at, pipeline_state):")
        for ps in physical_schemas:
            # Check assets table in this schema
            res = await conn.execute(text(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{ps}' AND table_name = 'assets'"))
            if res.fetchone():
                res = await conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_schema = '{ps}' AND table_name = 'assets'"))
                cols = [c[0] for c in res.fetchall()]
                missing = [c for c in ["rex_processed_at", "pipeline_state"] if c not in cols]
                if not missing:
                    print(f"  - {ps}.assets: ALIGNED (V51.5)")
                else:
                    print(f"  - {ps}.assets: DRIFT DETECTED (Missing: {missing})")
            else:
                print(f"  - {ps}: No 'assets' table found.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(full_map_audit())
