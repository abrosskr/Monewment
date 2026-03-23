import asyncio
import sys
from pathlib import Path
from sqlalchemy import text

sys.path.append(str(Path(__file__).resolve().parent.parent))
from core.database import engine

async def deep_audit():
    print("--- [DEEP AUDIT] V51.5 Structural Integrity Scan ---")
    
    expected_registry_cols = ["accumulated_cost", "budget_limit"]
    expected_asset_cols = ["rex_processed_at", "pipeline_state"]
    
    async with engine.connect() as conn:
        # 1. Audit Registry
        print("[1/2] Auditing schema_registry.stratums...")
        res = await conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'schema_registry' AND table_name = 'stratums'
        """))
        reg_cols = [r[0] for r in res.fetchall()]
        for col in expected_registry_cols:
            status = "OK" if col in reg_cols else "MISSING"
            print(f"  - {col}: {status}")

        # 2. Audit All Stratums
        print("[2/2] Auditing all Stratum assets tables...")
        res = await conn.execute(text("SELECT stratum_name FROM schema_registry.stratums"))
        stratums = [r[0] for r in res.fetchall()]
        
        for sname in stratums:
            schema = f"schema_stratum_{sname}"
            # Check if schema exists
            exists = await conn.execute(text(f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{schema}'"))
            if not exists.fetchone():
                print(f"  [!] {schema}: SCHEMA NOT FOUND (Physical drift detected)")
                continue
                
            res = await conn.execute(text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = '{schema}' AND table_name = 'assets'
            """))
            cols = [r[0] for r in res.fetchall()]
            print(f"  [*] {schema}.assets:")
            for col in expected_asset_cols:
                status = "OK" if col in cols else "MISSING"
                print(f"    - {col}: {status}")

        # 3. Check Pipeline Space
        print("[*] Auditing schema_pipeline...")
        res = await conn.execute(text("""
            SELECT table_name FROM information_schema.tables WHERE table_schema = 'schema_pipeline'
        """))
        tables = [r[0] for r in res.fetchall()]
        print(f"  - cross_reports: {'OK' if 'cross_reports' in tables else 'MISSING'}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(deep_audit())
