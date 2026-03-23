import asyncio
import httpx
import logging
import os
import sys
import uuid
import sqlite3
import importlib
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict
from core.config import settings # Core config

class QueenSettings(BaseSettings):
    """[V51.5] Queen-Specific Domain Configuration"""
    DOMAIN_HANDLER: str = ""
    LOCAL_REGISTRY_PATH: str = "local_registry.db"
    
    model_config = SettingsConfigDict(
        # Priority Chain: Core defaults first, then Local .env (CWD) overrides everything.
        env_file=[os.path.join(os.path.dirname(__file__), "..", ".env"), ".env"],
        env_file_encoding='utf-8',
        extra="ignore"
    )
queen_settings = QueenSettings()

class QueenGovernor:
    def __init__(self):
        # [DNA Locator Autonomy] Handled by DNA Linker Protocol at boot
        self._init_local_db() # [Mandate v3.0]
        self.logger = self._setup_logger()
        self.semaphore = asyncio.Semaphore(25)
        self.is_alive = True
        self.birth_time = datetime.now()
        # [V51.5] Decoupled: ID determined from environment or local_registry
        self.sovereign_id = os.getenv("QUEEN_ID") or f"QUEEN-{uuid.uuid4().hex[:8]}"
        self.fencing_token = None
        self.domain_handler = self._load_domain_handler()

    def _init_local_db(self):
        """[QUEEN Mandate v3.0] Auto-Initialization of Local Registry & WAL Mode"""
        conn = sqlite3.connect(queen_settings.LOCAL_REGISTRY_PATH, timeout=30)
        cursor = conn.cursor()
        # [V51.5] Infrastructure Mercy: Enable WAL Mode for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS local_registry (
                entity_id TEXT PRIMARY KEY,
                entity_type TEXT,
                status TEXT,
                current_cost REAL,
                last_heartbeat TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def _setup_logger(self):
        # Implementation should use core.logger.MaskedStream in real scenarios
        logging.basicConfig(
            level=settings.LOG_LEVEL,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(f"QUEEN-{settings.STRATUM_NAME.upper()}")

    def _load_domain_handler(self):
        handler_str = queen_settings.DOMAIN_HANDLER
        
        # [DEFENSIVE GUARD] Mandate v2.0
        if not handler_str or "." not in handler_str:
            self.logger.critical("Imperative Configuration Missing (DOMAIN_HANDLER)")
            self.logger.critical(f"Current Value: '{handler_str}'")
            sys.exit(1)
            
        try:
            module_path, class_name = handler_str.rsplit('.', 1)
            module = importlib.import_module(module_path)
            handler_class = getattr(module, class_name)
            return handler_class(self)
        except Exception as e:
            self.logger.critical(f"Failed to load DOMAIN_HANDLER: {e}")
            sys.exit(1)

    async def birth_ritual(self):
        """[Decree 1] Birth Sacrament (Identity Binding)"""
        self.logger.info("Initiating Birth Ritual...")
        # In a real implementation, this would call settings.MONEWMENT_URL/v1/registry/birth
        self.sovereign_id = f"QUEEN-ALLY-{settings.STRATUM_NAME.upper()}-01"
        self.fencing_token = f"FENCE-{self.sovereign_id}-{uuid.uuid4().hex[:8]}"
        self.logger.info(f"REJOICE! Sovereign ID 하사: {self.sovereign_id}")

    def update_local_registry(self, entity_id, entity_type, status, cost=0.0):
        """[QUEEN Mandate] Status Aggregation to local_registry.db"""
        try:
            # [V51.5] Increased timeout for busy DB scenarios
            conn = sqlite3.connect(queen_settings.LOCAL_REGISTRY_PATH, timeout=30)
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;") # Maintain WAL
            cursor.execute('''
                INSERT OR REPLACE INTO local_registry (entity_id, entity_type, status, current_cost, last_heartbeat)
                VALUES (?, ?, ?, ?, ?)
            ''', (entity_id, entity_type, status, cost, datetime.now().isoformat()))
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Failed to update local registry: {e}")

    async def execute_strategic_policy(self):
        """[Decree 4] Unified Work Loop"""
        self.logger.info(f"Starting Strategic Policy Loop for domain: {settings.STRATUM_NAME}")
        
        while True:
            try:
                # [V51.5] Mandatory Integrity Check
                self._check_lifetime()
                
                # Infrastructure Mercy: 10s Semaphore Timeout (Increased from 5s)
                async with asyncio.timeout(10.0):
                    async with self.semaphore:
                        await self.domain_handler.execute_logic()
                
                # Update global traces (traces) instead of direct reporting
                self.update_local_registry(self.sovereign_id, "QUEEN", "ACTIVE")
                
                # Mandated 5s delay for health
                await asyncio.sleep(5)
                self._check_lifetime()
                
            except asyncio.TimeoutError:
                self.logger.warning("503 Service Unavailable: DB Semaphore acquisition failed. Backing off.")
                await asyncio.sleep(10)
            except Exception as e:
                self.logger.error(f"Error in Strategic Policy Loop: {e}")
                await asyncio.sleep(5)

    async def honorable_seppuku(self, reason: str):
        """[QUEEN Mandate] Final termination routine (Self-Sacrifice)"""
        self.logger.critical(f"HONORABLE SEPPUKU: {reason}")
        self.is_alive = False
        # [NEW] Constitutional Mandate: Exit process strictly
        sys.exit(0)

    def _check_lifetime(self):
        """[V51.5] 72h Lifetime Enforcement (Article 6.1)"""
        elapsed = (datetime.now() - self.birth_time).total_seconds()
        if elapsed > 259200: # 72 hours
            self.logger.warning("72h LIFETIME EXCEEDED. Initiating auto-seppuku.")
            asyncio.create_task(self.honorable_seppuku("Lifetime expired"))

if __name__ == "__main__":
    # Internal test
    governor = QueenGovernor()
    asyncio.run(governor.execute_strategic_policy())
