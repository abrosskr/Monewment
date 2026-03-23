"""
MONEWMENT-0/routers/center.py — 공인 유니버셜 제국 API 센터 (UIAC)
[UIAC 3대 절대 강령 준수]
1. Seppuku: OS 레벨 psutil 강제 프로세스 종료 및 DB 트랜잭션 분리
2. Inventory: root_path 기반 비동기 local_registry.db 정찰
3. Security: 제국 관리자 전용 통제권 확보
"""

import os
import asyncio
import psutil
import sqlite3
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Any

from core.database import get_db
from core.logger import logger
from core.config import settings

router = APIRouter(prefix="/v1/center", tags=["Imperial Center (UIAC)"])

@router.post("/enforce/seppuku/{entity_id}", status_code=200)
async def enforce_seppuku(
    entity_id: str,
    pid: int = Query(..., description="OS Process ID of the target entity"),
    entity_type: str = Query("ant", description="ant | queen | stratum | areum"),
    x_local_gov_token: str = Header(..., alias="X-Local-Gov-Token"),
    db: AsyncSession = Depends(get_db)
):
    """[제국 사결 명령] DB 상태를 먼저 DEAD로 확정한 후, OS 프로세스를 처단한다."""
    if x_local_gov_token != settings.LOCAL_GOV_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden: Imperial Authority Required.")

    logger.critical(f"[UIAC] KILL ORDER ISSUED: Entity {entity_id} (PID: {pid})")

    table_map = {
        "ant": "schema_registry.ants",
        "queen": "schema_registry.queens",
        "stratum": "schema_registry.stratums",
        "areum": "schema_registry.areums"
    }
    table = table_map.get(entity_type.lower())
    if not table:
        raise HTTPException(status_code=400, detail="Invalid entity_type.")
    
    id_col = f"{entity_type.lower()}_id"
    
    # 1. DB 상태 확정 (OS 킬 실패 시에도 DB는 DEAD 유지)
    try:
        await db.execute(text(f"UPDATE {table} SET status = 'DEAD', death_reason = 'IMPERIAL_EXECUTION', died_at = NOW() WHERE {id_col} = :eid"), {"eid": entity_id})
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"[UIAC] Seppuku DB Update failed: {e}")
        raise HTTPException(status_code=500, detail=f"DB Execution Failed: {str(e)}")

    # 2. OS 레벨 프로세스 제거 (psutil)
    process_status = "TERMINATED"
    try:
        process = psutil.Process(pid)
        process.kill()
        logger.info(f"[UIAC] OS Process {pid} SUCCESSFULLY TERMINATED.")
    except psutil.NoSuchProcess:
        process_status = "ALREADY_DEAD"
        logger.warning(f"[UIAC] Process {pid} NOT FOUND. Already terminated.")
    except Exception as os_e:
        process_status = "OS_KILL_FAILED"
        logger.error(f"[UIAC] OS Kill Failed for PID {pid}: {os_e}")

    return {
        "status": "EXECUTED",
        "entity_id": entity_id,
        "pid": pid,
        "os_process_status": process_status,
        "message": "Entity executed. DB status updated to DEAD."
    }

async def scout_local_db(root_path: str) -> Dict[str, Any]:
    db_path = Path(root_path) / "local_registry.db"
    if not db_path.exists():
        return {"path": str(db_path), "status": "MISSING"}

    def read_db():
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM local_registry WHERE status = 'ACTIVE'")
            active_count = cursor.fetchone()[0]
            conn.close()
            return {"path": str(db_path), "status": "OPERATIONAL", "count": active_count}
        except Exception as e:
            return {"path": str(db_path), "status": "ERROR", "error": str(e)}

    return await asyncio.to_thread(read_db)

@router.get("/inventory")
async def get_imperial_inventory(
    x_local_gov_token: str = Header(..., alias="X-Local-Gov-Token"),
    db: AsyncSession = Depends(get_db)
):
    if x_local_gov_token != settings.LOCAL_GOV_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden: Imperial Authority Required.")

    result = await db.execute(text("SELECT stratum_id, stratum_name, root_path FROM schema_registry.stratums WHERE status != 'DEAD'"))
    stratums = result.fetchall()

    if not stratums:
        return {"stratums": [], "count": 0}

    scout_tasks = []
    scout_info_map = []
    for s in stratums:
        if s.root_path:
            scout_tasks.append(scout_local_db(s.root_path))
            scout_info_map.append({"id": str(s.stratum_id), "name": s.stratum_name})
        else:
            scout_info_map.append({"id": str(s.stratum_id), "name": s.stratum_name, "scout": "PATH_UNDEFINED"})

    results = await asyncio.gather(*scout_tasks)
    final_inventory = []
    scout_idx = 0
    for info in scout_info_map:
        if "scout" not in info:
            info["scout_result"] = results[scout_idx]
            scout_idx += 1
        final_inventory.append(info)

    return {"inventory_count": len(final_inventory), "stratums": final_inventory}
