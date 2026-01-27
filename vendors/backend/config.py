import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Core settings
    PROJECT_NAME: str = "VANDORS Antigravity"
    VERSION: str = "2.2.0"
    
    # Intelligence / LLM
    OLLAMA_API_URL: str = "http://localhost:11434/api/embeddings"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    
    # Evolution / Safety
    ENABLE_ONTOLOGY_EVOLUTION: bool = True
    
    # Paths
    # Default to a relative path from where the app runs, or absolute.
    # We use os.path.join to be safe relative to this file?
    # Or just simple string defaults.
    KNOWLEDGE_BASE_PATH: str = "backend/knowledge_base.json"
    
    # Data Storage
    # Default to 'data/fis_repo' inside the project directory for portability.
    # Can be overridden by FIS_REPO_PATH env var.
    FIS_DATA_PATH: str = os.path.join(os.getcwd(), "data", "fis_repo")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
