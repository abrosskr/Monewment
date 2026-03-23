import sys
import asyncio
import logging
from pathlib import Path
from sqlalchemy import text

# --- [V51.5 PATH RESOLUTION] ---
# MONEWMENT-0/core 패키지를 인식하도록 경로 설정
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from core.database import engine
from core.logger import logger

async def run_guardian():
    """
    'The Guardian' Self-Healing Migrator (V51.5)
    목표: 제국 전역의 스키마를 전수 조사하여 V51.5 필수 칼럼을 비파괴적으로 정렬한다.
    """
    print("\n" + "="*60)
    print("--- [V51.5] THE GUARDIAN: SELF-HEALING MIGRATOR START ---")
    print("="*60)
    
    report = []
    
    try:
        # 1. Registry Space Reconciliation
        print("\n[PHASE 1] Reconciling schema_registry (V51.5 Governance)...")
        async with engine.begin() as conn:
            # Stratums
            await conn.execute(text("""
                ALTER TABLE schema_registry.stratums 
                ADD COLUMN IF NOT EXISTS accumulated_cost FLOAT DEFAULT 0.0,
                ADD COLUMN IF NOT EXISTS budget_limit FLOAT DEFAULT 5.0;
            """))
            # Queens
            await conn.execute(text("""
                ALTER TABLE schema_registry.queens 
                ADD COLUMN IF NOT EXISTS accumulated_cost FLOAT DEFAULT 0.0,
                ADD COLUMN IF NOT EXISTS budget_limit FLOAT DEFAULT 5.0;
            """))
            # Ants
            await conn.execute(text("""
                ALTER TABLE schema_registry.ants 
                ADD COLUMN IF NOT EXISTS accumulated_cost FLOAT DEFAULT 0.0,
                ADD COLUMN IF NOT EXISTS budget_limit FLOAT DEFAULT 5.0;
            """))
            print("DONE: Registry attributes aligned.")
            report.append("| schema_registry (ALL) | ALIGNED |")
        
        # 2. Discovery: 모든 영토 명부 확보
        print("\n[PHASE 2] Discovering Stratums...")
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT stratum_name FROM schema_registry.stratums"))
            stratums = [row[0] for row in result.fetchall()]
        print(f"[*] Discovered {len(stratums)} active stratums in the registry.")
        
        # 3. Stratum Space Reconciliation
        print("\n[PHASE 3] Healing Individual Stratum Assets...")
        for name in stratums:
            schema = f"schema_stratum_{name}"
            print(f"[*] Checking {schema}...")
            try:
                async with engine.begin() as conn:
                    # REX 및 Pipeline 상태 칼럼 추가
                    await conn.execute(text(f"""
                        ALTER TABLE {schema}.assets 
                        ADD COLUMN IF NOT EXISTS rex_processed_at TIMESTAMP WITH TIME ZONE,
                        ADD COLUMN IF NOT EXISTS pipeline_state VARCHAR(50) DEFAULT 'RAW_DUMPED',
                        ADD COLUMN IF NOT EXISTS accumulated_cost FLOAT DEFAULT 0.0;
                    """))
                    print(f"   -> {schema} healed successfully.")
                    report.append(f"| {schema}.assets | ALIGNED |")
            except Exception as e:
                print(f"   -> [!] FAILED to heal {schema}: {e}")
                report.append(f"| {schema}.assets | FAILED: {str(e)[:30]}... |")
        
        # 4. Pipeline Space Reconciliation (Cross Reports)
        print("\n[PHASE 4] Reconciling schema_pipeline.cross_reports...")
        try:
            async with engine.begin() as conn:
                await conn.execute(text("""
                    ALTER TABLE schema_pipeline.cross_reports 
                    ADD COLUMN IF NOT EXISTS rex_processing BOOLEAN NOT NULL DEFAULT FALSE,
                    ADD COLUMN IF NOT EXISTS rex_processed_at TIMESTAMPTZ;
                """))
                print("DONE: Pipeline attributes aligned.")
                report.append("| schema_pipeline.cross_reports | ALIGNED |")
        except Exception as e:
            print(f"[!] Pipeline reconciliation failed: {e}")
            report.append("| schema_pipeline.cross_reports | FAILED |")

    except Exception as e:
        print(f"\n[CRITICAL ERROR] Guardian migration aborted: {e}")
        return

    print("\n" + "="*60)
    print("--- FINAL ALIGNMENT REPORT (Zero-Drift Audit) ---")
    print("-" * 60)
    print("| Target Table/Schema | Status |")
    print("|---------------------|--------|")
    for line in report:
        print(line)
    print("="*60)
    print("GLORY TO MONEWMENT.\n")

if __name__ == "__main__":
    # Windows Selector Event Loop Policy for compatibility
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(run_guardian())
