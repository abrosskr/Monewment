# 🏛️ Imperial Sentinel Rule: 100% Correct main.py (Synchronous Infra-Guard)
# c:\monewment\STRATUM\STRATUM-1\main.py

import os
import sys
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# [CORE IMPORT] Pure App Factory
from core.app_factory import create_app
from core.logger import logger
from core.config import settings
from core.robustness import ImperialGovernance

# [STRATUM SPECIFIC] Router & Dependencies
from routers import vendors, cctv, dashboard, pipeline
from queens.queen_legacy import QueenLegacyVendors

# [IDENTITY INJECTION] STRATUM-1 전용 백그라운드 태스크 정의
async def start_imperial_scout():
    """[V2.0 ACTIVE SCOUT — UIAC Integrated]"""
    from core.database import AsyncSessionLocal
    from sqlalchemy import text
    from datetime import datetime, timedelta, timezone
    
    KST = timezone(timedelta(hours=9))
    import sqlite3
    from pathlib import Path

    logger.info("[STRATUM-1] Active Scout Mission Initiated.")
    while True:
        try:
            async with AsyncSessionLocal() as db:
                now_kst = datetime.now(KST).replace(tzinfo=None)
                await db.execute(text("""
                    UPDATE schema_registry.ants SET status = 'DEAD', died_at = :now, death_reason = 'ORPHAN_TIMEOUT'
                    WHERE status = 'ACTIVE' AND last_seen_at < :threshold
                """), {"now": now_kst, "threshold": now_kst - timedelta(minutes=5)})
                await db.commit()
                # (Scouting logic continues...)
        except Exception as e:
            logger.error(f"[SCOUT] Scout Mission Interrupted: {e}")
        await asyncio.sleep(60)

async def start_queen_vendors():
    """Strategic Worker: QueenLegacyVendors"""
    logger.info("[STRATUM-1] Initializing Strategic Worker: QueenLegacyVendors")
    queen_legacy = QueenLegacyVendors()
    if await queen_legacy.connect():
        await queen_legacy.execute_task()

async def imperial_startup_sequence():
    """
    [V51.6 RECTIFIED] 통합 스타트업 시퀀스.
    비동기에 맡기지 않고 await로 인프라 가드를 먼저 처단한 후 정찰을 시작한다.
    """
    # 1. [CRITICAL] 인프라 물리 구조 검사 및 교정 (Synchronous Wait)
    from routers.pipeline import enforce_database_schema
    logger.info("[INFRA-GUARD] Blocking startup until database schema is synchronized...")
    await enforce_database_schema() 
    
    # 2. 백그라운드 태스크 기동
    asyncio.create_task(start_imperial_scout())
    asyncio.create_task(start_queen_vendors())

    # 3. [V9.2] 자가 심박 거버넌스 기동
    gov = ImperialGovernance(
        entity_type="stratum",
        entity_id=os.environ.get("STRATUM_ID", "badd8a15-5e63-4d24-81fd-489e8973cb85"),
        core_url="http://127.0.0.1:8800/v1",
        gateway_token=settings.GATEWAY_TOKEN
    )
    asyncio.create_task(gov.start_heartbeat())
    logger.info("[STRATUM-1] Imperial Heartbeat Governance Activated.")

# [FACTORY INHERITANCE] 코어 팩토리를 통해 앱 인스턴스 생성
app = create_app(
    stratum_id=os.environ.get("STRATUM_ID", "badd8a15-5e63-4d24-81fd-489e8973cb85"),
    extra_startup_task=imperial_startup_sequence
)

# [MANDATORY SURGERY] Core Pipeline Stitching
app.include_router(pipeline.router)

# [STRATUM-SPECIFIC ROUTERS] 영토 특화 라우터 수동 결합
app.include_router(vendors.router)
app.include_router(cctv.router)
app.include_router(dashboard.router)

# [STATIC CONTENT] 대시보드 및 정적 파일 마운트
static_path = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_path):
    os.makedirs(static_path)
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/health/stratum")
async def stratum_health():
    return {
        "status": "operational",
        "identity": "STRATUM-1",
        "core_dna": "V51.6 Pure-Core (Infra-Synchronized)"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info(f"[STRATUM-1] Imperial Ignition on Port 8800")
    uvicorn.run("main:app", host="0.0.0.0", port=8800, reload=True, access_log=False)
