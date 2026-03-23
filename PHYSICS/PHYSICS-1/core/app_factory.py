"""
MONEWMENT-0/core/app_factory.py — 제국의 '정신(Core DNA)'을 정의하는 순수 라이브러리.
모든 영토(Stratum)는 이 팩토리를 상속받아 자신의 개성(Router)을 주입한다.

[V51.5 Pure-Core Directive]
- No Identity (No STRATUM_ID/NAME in Core)
- Lifespan Injection (Supports extra_startup_task from Stratum)
- Global Imperial Protocols (Registry, Pipeline, DB Guard)
"""

import os
import asyncio
from typing import Optional, Callable, Awaitable
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from .config import settings
from .constants import HEADER_STRATUM_ID
from .logger import logger
from .registry import registry
from .provisioner import Provisioner
from .scheduler import run_gc_loop
from .security import system_cache
from .database import AsyncSessionLocal, engine
from sqlalchemy import text

def create_app(stratum_id: str, extra_startup_task: Optional[Callable[[], Awaitable[None]]] = None) -> FastAPI:
    """
    Core DNA가 주입된 FastAPI 인스턴스를 생성하여 반환함.
    
    Args:
        stratum_id: 해당 앱을 구동하는 영토의 식별자.
        extra_startup_task: STRATUM에서 주입하는 추가 비동기 시작 작업.
    """
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # [PHASE 1] Core Infrastructure Health Check
        logger.info(f"[GUARD] Initializing {stratum_id} — Performing Core Health Check...")
        from .db_guard import db_guard
        
        health_check_passed = False
        while not health_check_passed:
            try:
                await db_guard.check_and_wait()
                async with engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                db_guard.report_success()
                logger.info("[GUARD] Infrastructure Health Check PASSED. Resuming boot sequence.")
                health_check_passed = True
            except Exception as e:
                err_msg = str(e).lower()
                is_auth = "authentication" in err_msg or "password" in err_msg or "circuit breaker" in err_msg
                db_guard.report_failure(is_auth_error=is_auth)
                logger.warning(f"[GUARD] Health check failed, retrying: {e}")
                await asyncio.sleep(5)

        # [PHASE 2] Core Strategic Provisioning
        await Provisioner.create_system_space()    # 황실 행정
        await Provisioner.create_registry_space()  # 전사 레지스트리
        await Provisioner.create_pipeline_space()  # REX/AREUM 파이프라인

        # [PHASE 3] Core GC Scheduler
        asyncio.create_task(run_gc_loop())

        # [PHASE 4] Injection: Extra Startup Task from Stratum
        if extra_startup_task:
            logger.info(f"[INJECTION] Launching extra startup task for {stratum_id}...")
            asyncio.create_task(extra_startup_task())

        yield
        logger.info(f"System {stratum_id} Shutdown Initiated.")

    app = FastAPI(
        title=f"MONEWMENT Core - {stratum_id}",
        version=settings.VERSION,
        docs_url="/admin/docs",
        redoc_url="/admin/redoc",
        lifespan=lifespan
    )

    # [ROUTER] Imperial DNA (Registry, Pipeline, & Center)
    try:
        from routers import registry as registry_router, pipeline as pipeline_router, center as center_router
        app.include_router(registry_router.router)
        app.include_router(pipeline_router.router)
        app.include_router(center_router.router)
    except ImportError as e:
        logger.error(f"[CORE-FATAL] Fundamental DNA Routers not found: {e}")

    # [MIDDLEWARE] Global Kill Switch
    @app.middleware("http")
    async def kill_switch_middleware(request: Request, call_next):
        if await system_cache.get_status(AsyncSessionLocal):
            if request.url.path not in ("/health", "/admin/docs", "/admin/redoc"):
                return JSONResponse(
                    status_code=503, 
                    content={"status": "Global Shutdown Active", "retry_after": 60}
                )
        return await call_next(request)

    # [MIDDLEWARE] Stratum Routing & Alias Authentication
    @app.middleware("http")
    async def dispatch_stratum_middleware(request: Request, call_next):
        bypass_prefixes = ("/", "/health", "/v1/health", "/admin/docs", "/admin/redoc", 
                           "/openapi.json", "/favicon.ico", "/registry", "/v1/registry")
        if any(request.url.path == p or request.url.path.startswith(p + "/") for p in bypass_prefixes):
            return await call_next(request)

        # G1: X-Alias/Token Auth
        alias = request.headers.get("X-Alias")
        provided_token = request.headers.get("X-Queen-Token", "")
        if alias:
            if provided_token != settings.GATEWAY_TOKEN:
                return JSONResponse(status_code=403, content={"detail": "Forbidden: Invalid Gateway Token"})
            resolved = registry.resolve_alias(alias)
            if resolved:
                request.state.virtual_context = resolved

        # G3: Internal X-Stratum-ID Routing
        stratum_id_header = request.headers.get(HEADER_STRATUM_ID)
        if stratum_id_header:
            client_ip = request.client.host if request.client else "unknown"
            if client_ip in ("127.0.0.1", "::1", "localhost"):
                if registry.is_valid(stratum_id_header):
                    request.state.virtual_context = {"target_level": "STRATUM", "target_id": stratum_id_header}

        return await call_next(request)

    @app.get("/health")
    @app.get("/v1/health")
    async def core_health_check():
        return {
            "status": "operational",
            "version": settings.VERSION,
            "stratum_id": stratum_id,
            "mode": "Pure Imperial Core (Template)"
        }

    return app
