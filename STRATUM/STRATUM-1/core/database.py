# MONEWMENT-0/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from .config import settings

# [TECH SPEC COMPLIANCE]
# Port 6543 Transaction Mode requires strictly disabling prepared statements.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=20,
    max_overflow=10,
    connect_args={
        "prepared_statement_cache_size": 0, # Critical for Supabase Transaction Mode
        "statement_cache_size": 0,
        
    }
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session