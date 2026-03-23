import asyncio
import sys
from pathlib import Path
from sqlalchemy import text

sys.path.append(str(Path(__file__).resolve().parent.parent))
from core.database import engine

async def force_alignment():
    print("--- [FORCE ALIGNMENT] Healing Shadow & Legacy Schemas ---")
    
    # List of schemas that need manual intervention (discovered via audit)
    target_schemas = ["schema_stratum_vendors", "schema_stratum_test_1", "schema_stratum_test_2", "schema_stratum_test_3"]
    
    async with engine.connect() as conn:
        for schema in target_schemas:
            # Check if assets table exists
            res = await conn.execute(text(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}' AND table_name = 'assets'"))
            if res.fetchone():
                print(f"[*] Healing {schema}.assets...")
                async with engine.begin() as tx_conn:
                    await tx_conn.execute(text(f"ALTER TABLE {schema}.assets ADD COLUMN IF NOT EXISTS rex_processed_at TIMESTAMPTZ;"))
                    await tx_conn.execute(text(f"ALTER TABLE {schema}.assets ADD COLUMN IF NOT EXISTS pipeline_state VARCHAR DEFAULT 'RAW_DUMPED';"))
                print(f"  - {schema}.assets: ALIGNED.")
            else:
                print(f"  - {schema}: No assets table found, skipping.")

        # Also purge ghost records in registry (E2E_TEST ones with no physical schema)
        print("\n[*] Purging Ghost Registry Records (E2E_TEST)...")
        res = await conn.execute(text("SELECT stratum_name FROM schema_registry.stratums WHERE stratum_name LIKE 'E2E_TEST_%'"))
        ghost_names = [r[0] for r in res.fetchall()]
        
        for gname in ghost_names:
            schema = f"schema_stratum_{gname}"
            # Verify once more it doesn't exist physically
            res_ex = await conn.execute(text(f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{schema}'"))
            if not res_ex.fetchone():
                print(f"  - Purging {gname} (No physical schema found)")
                async with engine.begin() as tx_conn:
                    await tx_conn.execute(text("DELETE FROM schema_registry.stratums WHERE stratum_name = :n"), {"n": gname})

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(force_alignment())
