from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.core.config import settings

# [최적화] Supabase Transaction Pooler(6543) 환경을 위한 엔진 설정
engine = create_async_engine(
    settings.DATABASE_URL,
    # Supabase/PgBouncer 환경에서 Prepared Statement 충돌 방지 필수 설정
    connect_args={
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0
    },
    # 연결 유효성 검사 및 재사용 설정
    pool_pre_ping=True,      # 사용 전 연결 살아있는지 확인
    pool_recycle=300,        # 5분마다 연결 갱신 (Supabase 타임아웃 방지)
    echo=False,
    future=True
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)