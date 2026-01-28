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
    
    # Application Settings
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # CORS Settings
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    # Security Keys
    SECRET_KEY: str 
    ANT_ENCRYPTION_KEY: str  # 32-byte hex key for Ant encryption
    
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None

    REDIS_URL: str = "redis://localhost:6379/0"

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
    
    @computed_field
    def ALLOWED_ORIGINS_LIST(self) -> list[str]:
        """CORS 허용 도메인 리스트 반환"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    def validate_security_keys(self):
        """보안 키 검증"""
        if len(self.SECRET_KEY) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters. "
                "Generate one with: python scripts/generate_keys.py"
            )
        
        if len(self.ANT_ENCRYPTION_KEY) != 64:
            raise ValueError(
                "ANT_ENCRYPTION_KEY must be exactly 64 hex characters (32 bytes). "
                "Generate one with: python scripts/generate_keys.py"
            )
        
        # Validate hex format
        try:
            bytes.fromhex(self.ANT_ENCRYPTION_KEY)
        except ValueError:
            raise ValueError("ANT_ENCRYPTION_KEY must be a valid hex string")


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

# 시작 시 보안 키 검증
try:
    settings.validate_security_keys()
except ValueError as e:
    import sys
    print(f"❌ Configuration Error: {e}", file=sys.stderr)
    sys.exit(1)
