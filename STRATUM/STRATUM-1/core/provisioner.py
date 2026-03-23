import asyncio
from sqlalchemy import text
from .database import engine
from .logger import logger

class Provisioner:
    """[V9.0 ARCHITECTURE PURGE] Pure Infrastructure Provisioner"""

    @staticmethod
    async def ensure_schemas():
        """영토의 순수 물리 스키마만 선포한다. 데이터(지능) 주입은 절대 금지한다."""
        async with engine.begin() as conn:
            # 1. 영토 구조체 선포
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS schema_system;"))
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS schema_registry;"))
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS schema_pipeline;"))
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS schema_babel;"))

            # 2. 필수 인프라 테이블 (데이터 없이 구조만 생성)
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_system.system_config (
                    is_emergency_shutdown BOOLEAN DEFAULT FALSE,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """))
            
            # [IDEMPOTENCY] 중복 각인 방지용 레지스트리
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_registry.idempotency_keys (
                    key TEXT PRIMARY KEY,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """))
            
        logger.info("[V9.0] 🛡️ STRATUM-1 Infrastructure Purge & Schema Ensure Success.")

if __name__ == "__main__":
    asyncio.run(Provisioner.ensure_schemas())
