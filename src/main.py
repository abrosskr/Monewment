# src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.config import settings
from src.database import engine
from src.models import Base
from src.logger import setup_logger

# [신규] 우리가 방금 만든 라우터 가져오기
from src.routers import tools 

logger = setup_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 DB 테이블 생성
    logger.info("🚀 Starting up... Creating DB tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ DB Tables created successfully.")
    yield
    logger.info("🛑 Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

# [핵심] 여기서 라우터를 등록합니다.
# 결과적으로 /api/v1/tools/generate-tree 주소가 생성됩니다.
app.include_router(tools.router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {
        "system": "Monewment Cluster",
        "status": "active",
        "version": "4.1"
    }