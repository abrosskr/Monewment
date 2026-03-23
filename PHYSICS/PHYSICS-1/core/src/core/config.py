from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "monewment"
    DATABASE_URL: str = "postgresql+asyncpg://admin:password@localhost:5432/monewment"
    
    # Port Matrix
    HOST: str = "0.0.0.0"
    PORT_CORE_API: int = 8800
    PORT_TWIN_ENGINE: int = 8100
    PORT_ANT_ADAPTOR: int = 8200
    PORT_ADMIN_DASHBOARD: int = 8300
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
