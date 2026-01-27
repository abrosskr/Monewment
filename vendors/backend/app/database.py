from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 1. Database URL
# Defaults to SQLite but easily switched to PostgreSQL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# 2. Engine
# PostgreSQL doesn't need 'check_same_thread', only SQLite does
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base
Base = declarative_base()

# Utility Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
