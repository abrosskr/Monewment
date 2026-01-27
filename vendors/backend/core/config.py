from pydantic import Field
from pydantic_settings import BaseSettings
import os
from typing import List

class Settings(BaseSettings):
    # API Metadata
    PROJECT_NAME: str = "VANDORS Antigravity API"
    VERSION: str = "2.2.0"
    API_V1_STR: str = "/api"
    
    # Security
    API_KEY_NAME: str = "X-API-KEY"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-me")
    API_KEYS: List[str] = [os.getenv("FIS_MASTER_KEY", "fis-dev-2026-secret")]
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./vendors_local_v2.db")
    
    # Physics & FIS
    PHYSICS_DATA_PATH: str = os.getenv("PHYSICS_DATA_PATH", "data/ingredients_physics.json")
    
    # AI Models
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    EMBEDDING_MODEL: str = "nomic-embed-text"
    LLM_MODEL: str = "llama3"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
