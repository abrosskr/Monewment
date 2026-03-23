import asyncio
import sys
from pathlib import Path

# [DECREE 13] Path alignment
root = Path(__file__).resolve().parent.parent.parent
if str(root / "MONEWMENT-0") not in sys.path:
    sys.path.insert(0, str(root / "MONEWMENT-0"))

from sqlalchemy import text
from core.database import engine
from core.provisioner import Provisioner
from core.logger import logger

async def eradicate_entropy():
    logger.info("[MIGRATE] Starting Entropy Eradication V51.5...")
    
    # 1. Fix schema_registry.data_movements
    async with engine.begin() as conn:
        logger.info("[MIGRATE] Standardizing data_movements registry...")
        res = await conn.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_schema = 'schema_registry' AND table_name = 'data_movements'
        """))
        columns = [r[0] for r in res.fetchall()]
        
        if columns:
            if 'movement_id' in columns:
                await conn.execute(text("ALTER TABLE schema_registry.data_movements RENAME COLUMN movement_id TO id;"))
            if 'executed_at' in columns:
                await conn.execute(text("ALTER TABLE schema_registry.data_movements RENAME COLUMN executed_at TO timestamp;"))
            if 'source_location' not in columns:
                await conn.execute(text("ALTER TABLE schema_registry.data_movements ADD COLUMN source_location TEXT;"))
            if 'target_location' not in columns:
                await conn.execute(text("ALTER TABLE schema_registry.data_movements ADD COLUMN target_location TEXT;"))
            if 'sample_hash' not in columns:
                await conn.execute(text("ALTER TABLE schema_registry.data_movements ADD COLUMN sample_hash VARCHAR(64);"))
        else:
            await Provisioner.create_registry_space()

    # 2. Fix assets tables in all stratum schemas
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'schema_stratum_%'"))
        stratums = [r[0] for r in res.fetchall()]
    
    for schema in stratums:
        async with engine.begin() as conn:
            logger.info(f"[MIGRATE] Checking {schema}...")
            res = await conn.execute(text(f"SELECT 1 FROM information_schema.tables WHERE table_schema = '{schema}' AND table_name = 'assets'"))
            if not res.fetchone():
                continue
            
            res = await conn.execute(text(f"SELECT 1 FROM information_schema.columns WHERE table_schema = '{schema}' AND table_name = 'assets' AND column_name = 'rex_summary'"))
            if not res.fetchone():
                logger.info(f"[MIGRATE] Injecting rex_summary into {schema}.assets")
                await conn.execute(text(f"ALTER TABLE {schema}.assets ADD COLUMN rex_summary TEXT;"))

            res = await conn.execute(text(f"SELECT 1 FROM information_schema.columns WHERE table_schema = '{schema}' AND table_name = 'assets' AND column_name = 'rex_processed_at'"))
            if not res.fetchone():
                await conn.execute(text(f"ALTER TABLE {schema}.assets ADD COLUMN rex_processed_at TIMESTAMPTZ;"))

    # 3. Ensure Intelligence Spaces (REX/Pipeline)
    logger.info("[MIGRATE] Ensuring Intelligence Spaces (REX/Pipeline)...")
    await Provisioner.create_pipeline_space()
    await Provisioner.create_rex_space()
    await Provisioner.create_system_space()
    await Provisioner.create_archive_space()

    logger.info("[MIGRATE] Entropy Eradicated. 제국의 무결성이 회복되었습니다.")

if __name__ == "__main__":
    asyncio.run(eradicate_entropy())
