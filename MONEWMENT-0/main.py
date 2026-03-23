import os
import sys
import asyncio

# ==============================================================================
# 🚨 [DNA TEMPLATE - DO NOT RUN DIRECTLY IN PRODUCTION] 🚨
# This file is the Master DNA for MONEWMENT-0. 
# Deployed stratums should use their own main.py (e.g., STRATUM-1/main.py).
# Running this directly may cause registry duplication and scout conflicts.
# ==============================================================================
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# [CORE IMPORT] Pure App Factory
from core.app_factory import create_app
from core.logger import logger
from core.config import settings

# [STRATUM SPECIFIC] Router & Dependencies
from routers import vendors, cctv, dashboard, pipeline
# from queens.queen_legacy import QueenLegacyVendors

# [IDENTITY INJECTION] STRATUM-1 전용 백그라운드 태스크 정의
async def start_imperial_scout():
    """
    [V2.0 ACTIVE SCOUT — UIAC Integrated] 
    DB의 root_path를 기반으로 영토 내의 local_registry.db를 정찰하여 상태를 동기화함.
    """
    from core.database import AsyncSessionLocal
    from sqlalchemy import text
    import sqlite3
    from pathlib import Path
    from datetime import datetime

    logger.info("[STRATUM-1] Active Scout Mission Initiated: Scanning via Dynamic Root Paths.")
    
    while True:
        try:
            async with AsyncSessionLocal() as db:
                # 1. Guided Scout: 모든 영토의 root_path 조회
                res = await db.execute(text("SELECT stratum_id, stratum_name, root_path FROM schema_registry.stratums WHERE status != 'DEAD'"))
                stratums = res.fetchall()
                
                scanned_paths = set()
                guided_paths = []
                for s in stratums:
                    if s.root_path and os.path.exists(s.root_path):
                        guided_paths.append(Path(s.root_path))
                        scanned_paths.add(str(Path(s.root_path).resolve()))
                
                # 2. Wild Scout: 제국 표준 작업 디렉토리 스캔 (Constitutional Article 3.2)
                # 명시적 등록 없이도 Scout가 직접 발굴함.
                discovery_roots = [
                    Path("C:/monewment/PHYSICS"),
                    Path("C:/monewment/AREUM"),
                    Path("C:/monewment/MONEWMENT-0")
                ]
                
                for droot in discovery_roots:
                    if not droot.exists(): continue
                    # 1단계 하위 폴더까지만 탐색 (PHYSICS/PHYSICS-1 등)
                    for item in droot.iterdir():
                        if item.is_dir() and (item / "local_registry.db").exists():
                            if str(item.resolve()) not in scanned_paths:
                                guided_paths.append(item)
                                scanned_paths.add(str(item.resolve()))
                
                for r_path in guided_paths:
                    db_path = r_path / "local_registry.db"
                    s_display_name = r_path.name # Default to folder name
                    
                    if db_path.exists():
                        try:
                            # 2. 로컬 흔적 읽기 (SQLite)
                            def get_rows():
                                with sqlite3.connect(db_path) as conn:
                                    conn.row_factory = sqlite3.Row
                                    return conn.execute("SELECT * FROM local_registry").fetchall()
                            
                            rows = await asyncio.to_thread(get_rows)
                            
                            for row in rows:
                                # 3. 중앙 레지스트리 업데이트 (UPSERT)
                                row_dict = dict(row)
                                entity_type = row_dict['entity_type'].lower()
                                table_suffix = {"ant": "ants", "queen": "queens", "stratum": "stratums", "areum": "areums"}.get(entity_type, "ants")
                                table = f"schema_registry.{table_suffix}"
                                id_col = f"{entity_type}_id"
                                name_col = f"{entity_type}_name"
                                
                                # If it's a stratum row, update our display name
                                if entity_type == "stratum":
                                    s_display_name = row_dict.get("entity_name") or s_display_name

                                # Parse date string to datetime object
                                raw_date = row_dict.get("last_heartbeat") or row_dict.get("last_seen_at")
                                seen_at = None
                                if raw_date:
                                    try:
                                        seen_at = datetime.fromisoformat(raw_date)
                                    except Exception:
                                        seen_at = datetime.now()

                                await db.execute(text(f"""
                                    INSERT INTO {table} ({id_col}, {name_col}, status, last_seen_at, born_at)
                                    VALUES (:eid, :name, :status, :seen_at, :seen_at)
                                    ON CONFLICT ({id_col}) DO UPDATE
                                    SET status = EXCLUDED.status,
                                        last_seen_at = EXCLUDED.last_seen_at
                                """), {
                                    "status": row_dict["status"],
                                    "seen_at": seen_at,
                                    "eid": row_dict.get("entity_id") or row_dict.get("id"),
                                    "name": row_dict.get("entity_name") or f"DISCOVERED_{entity_type.upper()}_{str(row_dict.get('entity_id') or row_dict.get('id'))[:4]}"
                                })
                            
                            await db.commit()
                            logger.info(f"[SCOUT] Territory {s_display_name} state synchronized via {r_path}")
                        except Exception as te:
                            logger.warning(f"[SCOUT] Failed to scout trace at {r_path}: {te}")
            
        except Exception as e:
            logger.error(f"[SCOUT] Scout Mission Interrupted: {e}")
        
        await asyncio.sleep(settings.HEALTH_CHECK_INTERVAL)

# async def start_queen_vendors():
#     """
#     STRATUM-1의 특화 기능: 레거시 벤더 처리 Queen 기동.
#     """
#     logger.info("[STRATUM-1] Initializing Strategic Worker: QueenLegacyVendors")
#     queen_legacy = QueenLegacyVendors()
#     if await queen_legacy.connect():
#         await queen_legacy.execute_task()

async def imperial_startup_sequence():
    """V2.0 통합 스타트업 시퀀스"""
    asyncio.create_task(start_imperial_scout())
    # asyncio.create_task(start_queen_vendors())

# [FACTORY INHERITANCE] 코어 팩토리를 통해 앱 인스턴스 생성
app = create_app(
    stratum_id="STRATUM-1", 
    extra_startup_task=imperial_startup_sequence
)

# [STRATUM-SPECIFIC ROUTERS] 영토 특화 라우터 수동 결합
# Core DNA(Registry, Pipeline) 외에 STRATUM-1이 필요로 하는 기능들.
app.include_router(vendors.router)
app.include_router(cctv.router)
app.include_router(dashboard.router)

# [STATIC CONTENT] 대시보드 및 정적 파일 마운트 (영토 개별 책임)
static_path = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_path):
    os.makedirs(static_path)
app.mount("/static", StaticFiles(directory=static_path), name="static")

# [HEALTH OVERRIDE] 영토 특화 헬스체크 (필요시)
# [G3-EXCISION] Hidden dead endpoints removed by Imperial Decree.
@app.get("/health/stratum")
async def stratum_health():
    return {
        "status": "operational",
        "identity": "STRATUM-1",
        "core_dna": "V51.5 Pure-Core",
        "vantage": "Empire Primary Dispatcher"
    }

if __name__ == "__main__":
    import uvicorn
    # [V51.5 PORT PROTOCOL] 8800 포트 점유
    logger.info(f"[STRATUM-1] Imperial Ignition on Port 8800")
    uvicorn.run("main:app", host="0.0.0.0", port=8800, reload=True, access_log=True)
