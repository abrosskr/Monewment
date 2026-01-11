from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.config import settings

# 1. DB URL Handling for Async Driver
SQLALCHEMY_DATABASE_URL = getattr(settings, "DATABASE_URL", "postgresql://postgres:password@127.0.0.1:5433/monewment_db")
# print(f"DEBUG: Connecting to DB URL: {SQLALCHEMY_DATABASE_URL}") # Removed for security/cleanliness

# Force asyncpg driver if not present (for Docker/Local compatibility)
if SQLALCHEMY_DATABASE_URL.startswith("postgresql://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# 2. Async Engine Creation
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False, # Set to True for debugging SQL queries
    future=True,
    pool_pre_ping=True,
    pool_size=20,          # [Optimized] Keep 20 connections open
    max_overflow=10,       # [Optimized] Allow 10 more during spikes
    pool_recycle=3600,     # [Optimized] Recycle connections every hour
)

# 3. Async Session Factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Export for lifespan usage if needed
# But usually we use engine directly
