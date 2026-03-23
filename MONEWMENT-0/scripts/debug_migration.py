import sys
import asyncio
from pathlib import Path
from sqlalchemy import text

# Add parent directory to path to reach 'core'
sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.database import engine

async def debug_guardian():
    async with engine.begin() as conn:
        print("\n--- DEBUG: Pipeline Reconciliation ---")
        try:
            await conn.execute(text("""
                ALTER TABLE schema_pipeline.cross_reports 
                ADD COLUMN IF NOT EXISTS rex_processing BOOLEAN NOT NULL DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS rex_processed_at TIMESTAMPTZ;
            """))
            print("SUCCESS: Pipeline aligned.")
        except Exception as e:
            print(f"FAILURE: {e}")
            print(f"Exception Type: {type(e)}")

        print("\n--- DEBUG: Stratum-1 Reconciliation ---")
        try:
            await conn.execute(text("""
                ALTER TABLE schema_stratum_STRATUM_1.assets 
                ADD COLUMN IF NOT EXISTS rex_processed_at TIMESTAMP WITH TIME ZONE,
                ADD COLUMN IF NOT EXISTS pipeline_state VARCHAR(50) DEFAULT 'RAW_DUMPED';
            """))
            print("SUCCESS: STRATUM_1 aligned.")
        except Exception as e:
            print(f"FAILURE: {e}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(debug_guardian())
