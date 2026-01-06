from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import settings

# 1. DB URL 가져오기 (비동기 드라이버가 있다면 동기용으로 자동 변환)
# 1. DB URL 가져오기 (PostgreSQL on Port 5433)
# [TODO] 나중에 .env에서 로드하도록 변경 (Phase 1 완료 후)
db_url = "postgresql://user:monewment1234@localhost:5433/monewment"

# 2. 동기식 엔진 생성 (PostgreSQL)
engine = create_engine(
    db_url,
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
