import asyncio
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent
if str(root / "MONEWMENT-0") not in sys.path:
    sys.path.insert(0, str(root / "MONEWMENT-0"))

from sqlalchemy import text
from core.database import engine
from core.logger import logger

async def kill_sessions():
    logger.info("[EXECUTIONER] Terminating active database sessions...")
    async with engine.connect() as conn:
        # Get all PIDs except current
        await conn.execute(text("""
            SELECT pg_terminate_backend(pid) 
            FROM pg_stat_activity 
            WHERE datname = 'postgres' 
              AND pid <> pg_backend_pid()
              AND state IN ('active', 'idle In transaction');
        """))
        logger.info("[EXECUTIONER] Sessions terminated. Retrying migration immediately...")

if __name__ == "__main__":
    asyncio.run(kill_sessions())
