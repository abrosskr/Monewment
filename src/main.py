import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware 
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from prometheus_fastapi_instrumentator import Instrumentator

from src.config import settings
from src.database import engine
from src.models import Base
from src.core.logger import setup_logger
from src.core.redis_client import RedisManager
from src.core.scheduler import Scheduler
from src.middleware.request_id import RequestIDMiddleware
from src.collector import collector
from src.dependencies import get_db
from src.schemas import HealthCheckResponse

# [Refactor] New modules
from src.core.background import background_task_saver
from src.core.limiter import limiter

# Routers
from src.routers import tools, ui_factory, vcs
from src.api.v1.endpoints import auth, projects, services, chat, ant_socket, deploy, vm, billing, email_service
from src.api.v1.admin import dashboard, monitoring
from src.api.v1.sync import router as sync_router
from src.api.v1.vault import router as vault_router
from src.api.v1.render import router as render_router

logger = setup_logger()
running_processes = {}
background_tasks = {}
scheduler = Scheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting up... Checking Database Schema...")
    
    # [변경] Async Engine 사용 테이블 생성
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database Tables Verified (Async Mode).")
    except Exception as e:
        logger.critical(f"❌ DB Init Error: {e}")
        raise RuntimeError("Database initialization failed. Cannot start application.") from e

    # [신규] 수집기에 앱 인스턴스 주입
    collector.set_app(app)
    logger.info("✅ System Collector Attached.")

    await RedisManager.get_instance().connect()
    logger.info("✅ Redis Connected.")
    
    # [Phase 4.6] Multi-Cluster Manager Init
    from src.core.cluster_manager import ClusterManager
    await ClusterManager.get_instance().initialize()

    # [신규] Write-Behind Task Start
    task = asyncio.create_task(background_task_saver())
    background_tasks["saver"] = task

    yield
    
    # [신규] Cancel Background Task
    if "saver" in background_tasks:
        background_tasks["saver"].cancel()
        try:
            await background_tasks["saver"]
        except asyncio.CancelledError:
            pass

    # [신규] Redis Disconnection
    await RedisManager.get_instance().close()
    logger.info("🛑 Redis Connection Closed.")
    
    for name, proc in running_processes.items():
        proc.terminate()
    logger.info("🛑 Shutting down...")

app = FastAPI(title="Monewment Platform", version="4.8-Refactored", lifespan=lifespan)

# [Phase 2] Rate Limiting 설정
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/ping")
async def ping():
    return {"status": "pong"}

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
)

# [로깅 개선] 요청 추적 ID 미들웨어
app.add_middleware(RequestIDMiddleware)

# [모니터링] Prometheus 메트릭
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# [라우터 - Core]
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(dashboard.router, prefix="/api/admin", tags=["Admin Dashboard"])
app.include_router(monitoring.router, prefix="/api/admin/ants", tags=["Admin Monitoring"])
app.include_router(services.router, prefix="/api/services", tags=["Services"])
app.include_router(email_service.router, prefix="/api/services/email", tags=["Email Service"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI Agent"])

# [라우터 - WebSocket]
app.include_router(ant_socket.router, prefix="/ws/ant", tags=["Ant WebSocket"])

# [라우터 - Modules]
app.include_router(tools.router, prefix=settings.API_V1_STR)
app.include_router(ui_factory.router, prefix=f"{settings.API_V1_STR}/ui-factory", tags=["UI Factory"])
app.include_router(vcs.router, prefix=f"{settings.API_V1_STR}/vcs", tags=["VCS (Version Control Authority)"])
app.include_router(deploy.router, prefix=f"{settings.API_V1_STR}/deploy", tags=["Autonomous Deploy"])
app.include_router(vm.router, prefix="/api/vm", tags=["Virtual Machines"])
app.include_router(billing.router, prefix="/api/v1/billing", tags=["Billing & Payment"])
app.include_router(sync_router.router, prefix="/api/v1/sync", tags=["DeepSync (GenAI)"])
app.include_router(vault_router.router, prefix="/api/v1/vault", tags=["DeepVault (Storage)"])
app.include_router(render_router.router, prefix="/api/v1/render", tags=["DeepRender (Rendering)"])

@app.get("/")
def read_root():
    """시스템 헬스 체크 및 현재 가동 모드를 확인합니다."""
    return {"system": "Monewment Cluster", "status": "active", "mode": "B2B SaaS (Refactored)"}

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Integration Health Check"""
    checks = {
        "database": False,
        "redis": False,
    }
    
    # Database 체크
    try:
        await db.execute(select(1))
        checks["database"] = True
    except Exception as e:
        logger.error(f"Health Check - DB Error: {e}")
    
    # Redis 체크
    try:
        redis = RedisManager.get_instance().get_client()
        if redis:
            await redis.ping()
            checks["redis"] = True
    except Exception as e:
        logger.error(f"Health Check - Redis Error: {e}")
    
    if all(checks.values()):
        return HealthCheckResponse(
            status="healthy",
            checks=checks,
            timestamp=str(datetime.now())
        )
    else:
        raise HTTPException(
            status_code=503,
            detail=HealthCheckResponse(
                status="unhealthy",
                checks=checks,
                timestamp=str(datetime.now())
            ).dict()
        )

# System Collector APIs (Keep in main or move to admin/dashboard? Admin dashboard seems appropriate but collector usage here is simple enough to keep as 'meta' endpoints, or move to a 'meta' router. Let's keep them here for now to duplicate main.py functionality exactly, or attach them to dashboard if they overlap.)
# main.py had them at `/api/admin/schema` etc.
# I will attach them to dashboard router. 
# WAIT - Dashboard router is `src/api/v1/admin/dashboard.py`. I should move these there too!

# Correction: Move System Collector APIs to dashboard.py?
# Or just keep them in main.py if they are "System" level.
# Given the instruction to "Split", keeping them in main.py is bad.
# But `collector` usage is simpler here.
# Let's move them to `src/api/v1/admin/dashboard.py`.

# Re-reading my dashboard.py creation... I didn't include collector endpoints there.
# I will APPEND them to `src/api/v1/admin/dashboard.py` via `multi_replace`.
