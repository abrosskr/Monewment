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
engine_kwargs = {
    "echo": False,
    "future": True,
}

if not SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": 20,
        "max_overflow": 10,
        "pool_recycle": 3600,
    })

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)

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
