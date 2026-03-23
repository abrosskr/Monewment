import hashlib
import time
import os
import sys
import asyncio
from sqlalchemy import text

# Add project root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.database import AsyncSessionLocal
from core.config import settings
from core.logger import logger

STRATUM_ID = "badd8a15-5e63-4d24-81fd-489e8973cb85"

class GuardAnt:
    """
    The Sentinel (GUARD-ANT)
    Monitors system integrity and constitutional violations.
    """
    def __init__(self, ant_id="GUARD-SERVICE-MAIN"):
        self.ant_id = ant_id
        # Standardized paths relative to MONEWMENT-0
        self.target_dir = os.path.abspath("../.eden")
        self.hashes = {}
        
    async def register_self(self, status="ACTIVE"):
        """Register the GUARD in the imperial registry."""
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(text("""
                    INSERT INTO schema_registry.ants (ant_name, ant_type, status, stratum_id)
                    VALUES (:name, :type, :status, :sid)
                    ON CONFLICT (stratum_id, ant_name) DO UPDATE SET status = EXCLUDED.status
                """), {"name": self.ant_id, "type": "GUARD", "status": status, "sid": STRATUM_ID})
                await session.commit()
                logger.info(f"[REGISTRY] {self.ant_id} registered as {status}")
        except Exception as e:
            logger.error(f"[REGISTRY] Failed to register {self.ant_id}: {e}")

    def _get_hash(self, path: str) -> str:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def snapshot(self):
        """Creates a benchmark of current file hashes."""
        if os.path.exists(self.target_dir):
            for root, _, files in os.walk(self.target_dir):
                for file in files:
                    path = os.path.join(root, file)
                    self.hashes[path] = self._get_hash(path)
            logger.info(f"[GUARD] Baseline snapshot complete for {self.target_dir}")
        else:
            logger.warning(f"[GUARD] Target directory {self.target_dir} not found.")

    async def watch(self):
        """Infinite loop to detect mutations."""
        await self.register_self("ACTIVE")
        self.snapshot()
        
        while True:
            for path, old_hash in list(self.hashes.items()):
                if not os.path.exists(path):
                    logger.error(f"[VIOLATION] File DELETED: {path}")
                    continue
                
                new_hash = self._get_hash(path)
                if new_hash != old_hash:
                    logger.warning(f"[VIOLATION] Mutation detected in {path}")
            
            await asyncio.sleep(1) # Sovereign v3.0 Frequency

if __name__ == "__main__":
    # If ID is passed from spawn engine, use it
    current_id = "GUARD-SERVICE-MAIN"
    for i, arg in enumerate(sys.argv):
        if arg == "--id" and i + 1 < len(sys.argv):
            current_id = sys.argv[i+1]
            
    guard = GuardAnt(ant_id=current_id)
    asyncio.run(guard.watch())
