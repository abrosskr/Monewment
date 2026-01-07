# src/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    # Base directory of the project
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    
    # .env에 PROJECT_NAME이 있으면 그 값을 쓰고, 없으면 "Monewment"를 씁니다.
    PROJECT_NAME: str = "Monewment"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str 
    
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432

    GEMINI_API_KEY: str
    CLAUDE_API_KEY: Optional[str] = None

    # DeepRender Settings
    # Default: Assumes standard installation or PATH availability
    BLENDER_PATH: str = "C:\\Program Files\\Blender Foundation\\Blender 5.0\\blender.exe"

    # JWT Settings
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    @computed_field
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # 비동기 드라이버 asyncpg를 사용하는 주소 생성
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def PROJECTS_DIR(self) -> Path:
        return self.BASE_DIR / "projects"

    @property
    def TEMPLATES_DIR(self) -> Path:
        return self.BASE_DIR / "templates" / "standard"

    @property
    def ENV_FILE_PATH(self) -> Path:
        return self.BASE_DIR / ".env"

    # case_sensitive=True로 설정하여 .env의 대문자 변수명을 엄격하게 매칭합니다.
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        case_sensitive=True
    )

settings = Settings()