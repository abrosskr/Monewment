import asyncio
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent
if str(root / "MONEWMENT-0") not in sys.path:
    sys.path.insert(0, str(root / "MONEWMENT-0"))

from sqlalchemy import text
from core.database import engine
from core.provisioner import Provisioner
from core.logger import logger

async def force_eradicate_entropy():
    logger.info("[MIGRATE-FORCE] Starting Surgical Recovery...")
    
    # 1. Surgical Registry Update (Non-destructive)
    try:
        async with engine.begin() as conn:
            logger.info("[MIGRATE-FORCE] Attempting Registry column renames...")
            await conn.execute(text("SET statement_timeout = '5s';"))
            
            # Check current columns
            res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_schema='schema_registry' AND table_name='data_movements'"))
            cols = [r[0] for r in res.fetchall()]
            
            if 'movement_id' in cols:
                await conn.execute(text("ALTER TABLE schema_registry.data_movements RENAME COLUMN movement_id TO id;"))
            if 'executed_at' in cols:
                await conn.execute(text("ALTER TABLE schema_registry.data_movements RENAME COLUMN executed_at TO timestamp;"))
            
            # Ensure missing columns exist
            for col in ['source_location', 'target_location', 'sample_hash']:
                if col not in cols:
                    await conn.execute(text(f"ALTER TABLE schema_registry.data_movements ADD COLUMN {col} TEXT;"))
    except Exception as e:
        logger.warning(f"[MIGRATE-FORCE] Registry update skipped/failed (likely locked): {e}")

    # 2. Asset Modernization (Critical)
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'schema_stratum_%'"))
        stratums = [r[0] for r in res.fetchall()]
    
    for schema in stratums:
        try:
            async with engine.begin() as conn:
                logger.info(f"[MIGRATE-FORCE] Patching {schema}.assets...")
                res = await conn.execute(text(f"SELECT 1 FROM information_schema.tables WHERE table_schema='{schema}' AND table_name='assets'"))
                if not res.fetchone(): continue
                
                await conn.execute(text(f"SET statement_timeout = '10s';"))
                
                # ai_summary (AREUM Output)
                res = await conn.execute(text(f"SELECT 1 FROM information_schema.columns WHERE table_schema='{schema}' AND table_name='assets' AND column_name='ai_summary'"))
                if not res.fetchone():
                    await conn.execute(text(f"ALTER TABLE {schema}.assets ADD COLUMN ai_summary TEXT;"))

                # rex_summary (REX Output)
                res = await conn.execute(text(f"SELECT 1 FROM information_schema.columns WHERE table_schema='{schema}' AND table_name='assets' AND column_name='rex_summary'"))
                if not res.fetchone():
                    await conn.execute(text(f"ALTER TABLE {schema}.assets ADD COLUMN rex_summary TEXT;"))
                
                # rex_processed_at
                res = await conn.execute(text(f"SELECT 1 FROM information_schema.columns WHERE table_schema='{schema}' AND table_name='assets' AND column_name='rex_processed_at'"))
                if not res.fetchone():
                    await conn.execute(text(f"ALTER TABLE {schema}.assets ADD COLUMN rex_processed_at TIMESTAMPTZ;"))
        except Exception as e:
            logger.error(f"[MIGRATE-FORCE] Failed to patch {schema}: {e}")

    # 3. Ensure Intelligence Spaces
    logger.info("[MIGRATE-FORCE] Ensuring Intelligence Spaces...")
    try:
        await Provisioner.create_pipeline_space()
        await Provisioner.create_rex_space()
        await Provisioner.create_system_space()
    except Exception as e:
         logger.error(f"[MIGRATE-FORCE] Provisioning error: {e}")

    logger.info("[MIGRATE-FORCE] Surgical Recovery complete. 제국의 무결성이 부분적으로 회복되었습니다.")

if __name__ == "__main__":
    asyncio.run(force_eradicate_entropy())
