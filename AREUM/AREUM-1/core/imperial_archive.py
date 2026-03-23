import asyncio
import os
import sys
import logging
from datetime import datetime
from sqlalchemy import text, select, func
from sqlalchemy.ext.asyncio import create_async_engine

# [DECREE 10.3] Absolute environment anchoring
BASE_DIR = r"c:\forager"
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
os.chdir(BASE_DIR)

from backend.app.core.config import settings
from backend.app.core.db_utils import create_imperial_engine

# Path fix for AuditLogger
sys.path.insert(0, str(Path(r"c:\monewment\MONEWMENT-0")))
from core.audit_logger import AuditLogger

logging.basicConfig(level=logging.INFO, format="[IMPERIAL-ARCHIVE] %(levelname)s: %(message)s")
logger = logging.getLogger("archive")

async def run_archive_cycle():
    """
    [DECREE 11: ETERNAL ASSET]
    Incremental backup from schema_stratum_vendors.raw_archive to schema_archive.eternal_assets.
    """
    logger.info("[ARCHIVE] Starting Imperial Persistence Cycle...")
    engine = create_imperial_engine()
    
    async with engine.begin() as conn:
        # 1. Identify missing assets
        # We use content_hash as the symmetry key
        logger.info("[ARCHIVE] Syncing assets from Vendors Stratum to Archive Vault...")
        
        await conn.execute(text("""
            INSERT INTO schema_archive.eternal_assets (original_id, url, content_hash, raw_html_gz)
            SELECT id, url, content_hash, raw_html_gz
            FROM schema_stratum_vendors.raw_archive src
            WHERE NOT EXISTS (
                SELECT 1 FROM schema_archive.eternal_assets dst 
                WHERE dst.content_hash = src.content_hash
            );
        """))
        
        # 2. Count metrics
        res = await conn.execute(text("SELECT count(*) FROM schema_archive.eternal_assets;"))
        total = res.scalar()
        logger.info(f"[ARCHIVE] Cycle Complete. Total Eternal Assets Secured: {total}")
        
        # [DECREE 13] 아카이브 수행 이력 기록
        await AuditLogger.log_movement(
            action_type="SYNC-ARCHIVE",
            source="schema_stratum_vendors.raw_archive",
            target="schema_archive.eternal_assets",
            count=total,
            reason="Periodic Imperial Persistence Cycle"
        )

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_archive_cycle())
