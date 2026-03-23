# 📜 Imperial Core Router — Registry v5.0 (Aggressive Identity Fix)
# c:\monewment\STRATUM\STRATUM-1\routers\registry.py

from fastapi import APIRouter, Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from core.database import get_db
from core.logger import logger
from core.repository_registry import RegistryRepository
from core.models_registry import BirthRequest, PingRequest
from core.config import settings
from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))

router = APIRouter(prefix="/v1/registry", tags=["Registry v5"])

_TABLE_MAP = {
    "monewment": "schema_registry.monewments",
    "stratum":   "schema_registry.stratums",
    "queen":     "schema_registry.queens",
    "ant":       "schema_registry.ants",
    "areum":     "schema_registry.areums",
    "physics":   "schema_registry.ants"
}

@router.post("/birth", status_code=200)
async def entity_birth(
    body: BirthRequest,
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db)
):
    """[MIGRATION] 엔티티 탄생성사 — 공격적 ID 추출기(Aggressive ID Extractor) 적용"""
    entity_type = body.entity_type.lower()
    payload = body.payload
    
    # [CRITICAL FIX] Aggressive ID Extractor
    target_id = (
        getattr(body, "entity_id", None) or 
        payload.get(f"{entity_type}_id") or 
        payload.get("entity_id") or 
        payload.get("id") or 
        payload.get("worker_id") or
        payload.get("queen_id")
    )
    if target_id and str(target_id).strip() != "":
        payload[f"{entity_type}_id"] = str(target_id)
        payload["entity_id"] = str(target_id)
    else:
        # ID가 없는 경우 자동 생성은 금지하며 예외를 던짐 (제국 헌법 제2절)
        raise HTTPException(status_code=400, detail=f"No valid ID found in payload for {entity_type}")

    repo = RegistryRepository(db)
    async with db.begin():
        try:
            if entity_type == "monewment":
                result = await repo.birth_monewment(payload)
            elif entity_type == "stratum":
                result = await repo.birth_stratum(payload)
            elif entity_type == "queen":
                result = await repo.birth_queen(payload)
            elif entity_type == "areum":
                result = await repo.birth_areum(payload)
            else: # ant, physics
                result = await repo.birth_ant(payload)

            return {
                "status": "BORN",
                "entity_type": entity_type,
                "entity_id": result["entity_id"],
                "official_name": result.get("official_name"),
                "born_at": result.get("born_at")
            }
        except Exception as e:
            logger.error(f"[REGISTRY-DIAG] Birth Failed for {entity_type}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

@router.patch("/ping/{entity_type}/{entity_id}")
async def entity_ping(entity_type: str, entity_id: str, db: AsyncSession = Depends(get_db)):
    """[MIGRATION] 하트비트 — String 기반 비교 (Universal ID 대응)"""
    etype = entity_type.lower()
    table = _TABLE_MAP.get(etype)
    if not table:
        raise HTTPException(status_code=400, detail=f"Unknown entity type: {etype}")

    id_col = f"{etype}_id" if etype in ["monewment", "stratum", "queen", "areum"] else "ant_id"

    try:
        now_kst = datetime.now(KST).replace(tzinfo=None)
        async with db.begin():
            # [MANDATE] ::text 기반 조회 (Universal ID 대응)
            q = text(f"""
                UPDATE {table} 
                SET last_seen_at = :now, status = 'ACTIVE' 
                WHERE {id_col}::text = :eid
            """)
            result = await db.execute(q, {"eid": entity_id, "now": now_kst})
            if result.rowcount == 0:
                logger.warning(f"[REGISTRY-DIAG] Ping Target Not Found: {etype} {entity_id}")
                raise HTTPException(status_code=404, detail="Entity not found")
            
        return {"entity_id": entity_id, "status": "ACTIVE"}
    except Exception as e:
        logger.error(f"[REGISTRY-DIAG] Ping Failed for {entity_id}: {e}")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/death/{entity_type}/{entity_id}")
async def entity_death(entity_type: str, entity_id: str, x_local_gov_token: str | None = Header(None, alias="X-Local-Gov-Token"), db: AsyncSession = Depends(get_db)):
    if x_local_gov_token != settings.LOCAL_GOV_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    etype = entity_type.lower()
    table = _TABLE_MAP.get(etype)
    pk = f"{etype}_id" if etype in ["monewment", "stratum", "queen", "areum"] else "ant_id"
    
    now_kst = datetime.now(KST)
    async with db.begin():
        res = await db.execute(text(f"UPDATE {table} SET status = 'DEAD', died_at = :now WHERE {pk}::text = :eid"), {"eid": entity_id, "now": now_kst})
        if res.rowcount == 0:
            raise HTTPException(status_code=404, detail="Not found")
    return {"status": "DEAD", "entity_id": entity_id}

@router.get("/list/{entity_type}")
async def entity_list(entity_type: str, limit: int = 100, db: AsyncSession = Depends(get_db)):
    etype = entity_type.lower()
    table = _TABLE_MAP.get(etype)
    res = await db.execute(text(f"SELECT * FROM {table} ORDER BY born_at DESC LIMIT :limit"), {"limit": limit})
    return {"items": [dict(r._mapping) for r in res.fetchall()]}
