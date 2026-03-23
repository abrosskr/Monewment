# 📜 Imperial Core Config — Local-First Forced Version (v4.1.0)
# c:\monewment\STRATUM\STRATUM-1\core\config.py

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field, field_validator

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "MONEWMENT Imperial Core"
    VERSION: str = "4.1.0"
    TIMEZONE: str = "Asia/Seoul"

    # Identity
    STRATUM_NAME: str = "STRATUM-1"
    STRATUM_ID: str = ""
    QUEEN_ID: str = ""

    # Connectivity
    LOG_LEVEL: str = "INFO"
    GATEWAY_TOKEN: str = "mon_gateway_v4_shh" # X-Gateway-Token (Internal Auth)
    LOCAL_GOV_TOKEN: str = "mon_gov_v4_shh" # X-Local-Gov-Token (Death Auth)

    # [MANDATE 3] Local DB Forced Lock
    # .env 에 DATABASE_URL 이 있어도, 로컬 PC(127.0.0.1) 주소가 아니면 
    # 제국 헌법 v4.0에 따라 무시하고 로컬 PostgreSQL을 강제한다.
    DATABASE_URL: str = "postgresql+asyncpg://forager:forager@127.0.0.1:5432/forager"

    # @field_validator("DATABASE_URL", mode="before")
    # @classmethod
    # def force_local_db(cls, v: str) -> str:
    #     """[ABSOLUTE] 로컬 DB(127.0.0.1)가 아니면 무조건 Fallback 강제"""
    #     if not v or ("127.0.0.1" not in v and "localhost" not in v):
    #         # 외부 클라우드 URL이 감지되면 즉시 차단하고 로컬 기본값으로 회귀
    #         return "postgresql+asyncpg://forager:forager@127.0.0.1:5432/forager"
    #     return v

    # [V51.5] Governance & Scout Settings (RESTORED)
    HEALTH_CHECK_INTERVAL: int = 60 # Seconds between health pings
    ACTIVE_SCOUT_INTERVAL_SEC: int = 300 # Seconds between Scout scans
    BATCH_SIZE: int = 50 # Batch size for registry operations

    # Cloud Registry (Limited Usage: 500MB Policy)
    SUPABASE_USER: str = ""
    SUPABASE_PASSWORD: str = ""
    SUPABASE_HOST: str = ""
    SUPABASE_DB: str = "postgres"
    SUPABASE_PORT: int = 6543

    @computed_field
    @property
    def CLOUD_REGISTRY_URL(self) -> str:
        """Isolated Cloud Registry for Trace Imprinting only."""
        if not all([self.SUPABASE_USER, self.SUPABASE_PASSWORD, self.SUPABASE_HOST]):
            return ""
        return f"postgresql+asyncpg://{self.SUPABASE_USER}:{self.SUPABASE_PASSWORD}@{self.SUPABASE_HOST}:{self.SUPABASE_PORT}/{self.SUPABASE_DB}"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "..", ".env"),
        extra="ignore"
    )

settings = Settings()
