from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import settings

# 1. DB URL 가져오기 (비동기 드라이버가 있다면 동기용으로 자동 변환)
db_url = getattr(settings, "DATABASE_URL", "sqlite:///./monewment.db")
if "sqlite+aiosqlite" in db_url:
    db_url = db_url.replace("sqlite+aiosqlite", "sqlite")

# 2. 동기식 엔진 생성 (Standard)
engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
    echo=False,
    pool_pre_ping=True,
    future=True
)

# 3. 세션 팩토리 (Sync Session)
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)
