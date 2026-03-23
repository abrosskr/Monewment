# 📜 Imperial Core Config — Local-First Forced Version (v4.1.0)
# c:\monewment\MONEWMENT-0\core\config.py

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field, field_validator

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "MONEWMENT Iron Triangle"
    VERSION: str = "4.1.0"
    TIMEZONE: str = "Asia/Seoul"

    # Identity
    STRATUM_NAME: str = "vendors"
    STRATUM_ID: str = "STRATUM-0"
    QUEEN_ID: str = ""

    # Connectivity
    MONEWMENT_URL: str = "http://localhost:8800"
    EDENVALE_URL: str = "http://localhost:8801"
    REDIS_URL: str = "redis://localhost:6379/0"
    LOG_LEVEL: str = "INFO"
    GATEWAY_TOKEN: str = "mon_gateway_v4_shh"
    LOCAL_GOV_TOKEN: str = "mon_gov_v4_shh"

    # [MANDATE 3] Local DB Forced Lock
    DATABASE_URL: str = "postgresql+asyncpg://forager:forager@127.0.0.1:5432/forager"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def force_local_db(cls, v: str) -> str:
        """[ABSOLUTE] 로컬 DB(127.0.0.1)가 아니면 무조건 Fallback 강제"""
        if not v or ("127.0.0.1" not in v and "localhost" not in v):
            return "postgresql+asyncpg://forager:forager@127.0.0.1:5432/forager"
        return v

    # [V51.5] Governance & Scout Settings
    HEALTH_CHECK_INTERVAL: int = 60
    ACTIVE_SCOUT_INTERVAL_SEC: int = 300
    BATCH_SIZE: int = 50

    # Cloud Registry (500MB Policy 격리)
    SUPABASE_USER: str = ""
    SUPABASE_PASSWORD: str = ""
    SUPABASE_HOST: str = ""
    SUPABASE_DB: str = "postgres"
    SUPABASE_PORT: int = 6543

    @computed_field
    @property
    def CLOUD_REGISTRY_URL(self) -> str:
        if not all([self.SUPABASE_USER, self.SUPABASE_PASSWORD, self.SUPABASE_HOST]):
            return ""
        return f"postgresql+asyncpg://{self.SUPABASE_USER}:{self.SUPABASE_PASSWORD}@{self.SUPABASE_HOST}:{self.SUPABASE_PORT}/{self.SUPABASE_DB}"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "..", ".env"),
        extra="ignore"
    )

settings = Settings()