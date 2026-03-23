"""
routers/registry.py — API Contract v2.0
New: /v1/ prefix, Idempotency-Key, fencing_token, cursor pagination,
     DeathRequest with reason, /materialize endpoint, 409 rebirth check
"""
from fastapi import APIRouter, Header, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from core.database import get_db
from core.logger import logger
from core.repository_registry import RegistryRepository
from core.models_registry import BirthRequest, PingRequest, DeathRequest, MaterializeRequest

router = APIRouter(prefix="/v1/registry", tags=["Registry v1"])

_ALLOWED_TYPES = {"monewment", "stratum", "queen", "ant", "areum"}


# ─── Birth ───────────────────────────────────────────────────────────────────
@router.post("/birth", status_code=200)
async def entity_birth(
    body: BirthRequest,
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db)
):
    """엔티티 탄생 등록 — API Contract v2.0 (Idempotency-Key, UNIQUE check)"""
    entity_type = body.entity_type.lower()
    if entity_type not in _ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Unknown entity_type: {entity_type!r}")

    # [Contract #1] Idempotency-Key 중복 체크 (72시간 보관)
    if idempotency_key:
        result = await db.execute(text("""
            SELECT entity_id, entity_type FROM schema_registry.idempotency_keys
            WHERE idempotency_key = :key
        """), {"key": idempotency_key})
        existing = result.fetchone()
        if existing:
            # [V51.5] Also fetch the current fencing_token for idempotent hits
            token_res = await db.execute(text(f"SELECT fencing_token FROM schema_registry.{existing.entity_type}s WHERE {existing.entity_type}_id = :eid"), {"eid": existing.entity_id})
            token_row = token_res.fetchone()
            current_token = token_row[0] if token_row else 1

            logger.info(f"[REGISTRY] Idempotency-Key hit: {idempotency_key} → {existing.entity_id} (Token: {current_token})")
            return {
                "status": "BORN",
                "entity_type": existing.entity_type,
                "entity_id": str(existing.entity_id),
                "fencing_token": current_token,
                "idempotent": True
            }

    repo = RegistryRepository(db)
    result_map = {"db": "FAILED", "material": "SKIPPED", "registry_doc": "SKIPPED", "manifest": "SKIPPED"}

    try:
        if entity_type == "monewment":
            result = await repo.birth_monewment(body.payload)
        elif entity_type == "stratum":
            result = await repo.birth_stratum(body.payload)
            # [Dynamic Provisioning] 실제 물리 DB 스키마 생성 트리거
            from core.provisioner import Provisioner
            await Provisioner.create_stratum_space(body.payload["stratum_name"])
        elif entity_type == "queen":
            result = await repo.birth_queen(body.payload)
        elif entity_type == "areum":
            result = await repo.birth_areum(body.payload)
        else:  # ant
            result = await repo.birth_ant(body.payload)

        await db.commit()
        result_map["db"] = "OK"
        entity_id = result["entity_id"]

        # [Contract #1] Idempotency-Key 저장
        if idempotency_key:
            await db.execute(text("""
                INSERT INTO schema_registry.idempotency_keys (idempotency_key, entity_id, entity_type)
                VALUES (:key, :eid, :etype) ON CONFLICT DO NOTHING
            """), {"key": idempotency_key, "eid": entity_id, "etype": entity_type})
            await db.commit()

        logger.info(f"[REGISTRY] Birth: {entity_type} → {entity_id} (Official: {result.get('official_name', 'N/A')})")
        return {
            "status": "BORN",
            "entity_type": entity_type,
            "entity_id": entity_id,
            "official_name": result.get("official_name"), # 발급된 공식 이름 반환 (QUEEN, ANT 등)
            "fencing_token": result.get("fencing_token", 1),
            "born_at": result.get("born_at"),
            "result_map": result_map
        }

    except Exception as e:
        err = str(e)
        # [Contract #2] UNIQUE violation → 409 Conflict
        if "unique" in err.lower() or "duplicate" in err.lower():
            raise HTTPException(status_code=409, detail=f"Entity already exists (ACTIVE/DORMANT). Kill it first or use Idempotency-Key.")
        logger.error(f"[REGISTRY] Birth failed: {err}")
        raise HTTPException(status_code=500, detail=err)


# ─── Ping ────────────────────────────────────────────────────────────────────
@router.patch("/ping/{entity_type}/{entity_id}")
async def entity_ping(
    entity_type: str,
    entity_id: str,
    body: PingRequest | None = None,
    db: AsyncSession = Depends(get_db)
):
    """Heartbeat — last_seen_at 갱신 + fencing_token 반환"""
    if entity_type.lower() not in _ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Unknown entity_type: {entity_type!r}")

    table = f"schema_registry.{entity_type.lower()}s"
    id_col = f"{entity_type.lower()}_id"

    try:
        # [V51.5 Fortification] Robust UUID parsing to prevent 500 errors on reserved/non-UUID IDs
        import uuid
        try:
            uuid.UUID(entity_id)
        except ValueError:
            logger.warning(f"[REGISTRY] Non-UUID ping attempted for {entity_type}/{entity_id}. Bypassing DB update.")
            return {
                "entity_id": entity_id,
                "status": "ACTIVE",
                "note": "Bypassed registry update (non-UUID identity)."
            }

        # [Contract: Fencing Token] 단조 증가 — 좀비 프로세스 차단
        result = await db.execute(text(f"""
            UPDATE {table}
            SET last_seen_at = NOW(),
                status = CASE WHEN status IN ('DORMANT', 'IDLE', 'RUNNING') THEN 'ACTIVE' ELSE status END,
                fencing_token = fencing_token + 1
            WHERE {id_col} = :eid AND status != 'DEAD'
            RETURNING fencing_token, status, last_seen_at
        """), {"eid": entity_id})
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found or already DEAD.")

        await db.commit()

        # [FORTIFICATION] V51.5 Governance: Cost Accumulation & Kill Order
        session_cost = body.current_session_cost if body else 0.0
        
        # 1. Update DB with accumulated cost
        await db.execute(text(f"""
            UPDATE {table}
            SET accumulated_cost = accumulated_cost + :scost
            WHERE {id_col} = :eid
        """), {"scost": session_cost, "eid": entity_id})
        
        # 2. Check budget gating
        budget_check = await db.execute(text(f"""
            SELECT accumulated_cost, budget_limit FROM {table} WHERE {id_col} = :eid
        """), {"eid": entity_id})
        budget_row = budget_check.fetchone()
        
        if budget_row and (budget_row.accumulated_cost or 0) > (budget_row.budget_limit or 1000000000.0):
            logger.warning(f"[REGISTRY] KILL_ORDER Issued to {entity_type}/{entity_id} - Accumulated {budget_row.accumulated_cost} > {budget_row.budget_limit}")
            await db.execute(text(f"UPDATE {table} SET status = 'DEAD', death_reason = 'COST_CAP', died_at = NOW() WHERE {id_col} = :eid"), {"eid": entity_id})
            await db.commit()
            return {
                "status": "KILL_ORDER",
                "reason": "Budget Exceeded",
                "entity_id": entity_id
            }

        await db.commit()
        logger.info(f"[REGISTRY] Ping: {entity_type}/{entity_id} token={row.fencing_token} (AccCost: {budget_row.accumulated_cost if budget_row else 'N/A'})")

        logger.info(f"[REGISTRY] Ping: {entity_type}/{entity_id} token={row.fencing_token}")
        return {
            "entity_id": entity_id,
            "status": row.status,
            "last_seen_at": str(row.last_seen_at),
            "fencing_token": row.fencing_token
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Death ───────────────────────────────────────────────────────────────────
from core.config import settings

@router.delete("/death/{entity_type}/{entity_id}")
async def entity_death(
    entity_type: str,
    entity_id: str,
    body: DeathRequest | None = None,
    x_local_gov_token: str | None = Header(None, alias="X-Local-Gov-Token"),
    db: AsyncSession = Depends(get_db)
):
    """엔티티 사망 등록 — reason + final_cost_cents 기록"""
    # [V40 Contract: Death Auth] Only Local Government (MONEWMENT-n) can declare death.
    if x_local_gov_token != settings.LOCAL_GOV_TOKEN:
        logger.warning(f"[REGISTRY GUARD] Unauthorized DEATH attempt on {entity_id} - requires Local Gov Token.")
        raise HTTPException(status_code=403, detail="Forbidden: Only Local Government (MONEWMENT-n) can declare DEATH.")

    if entity_type.lower() not in _ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Unknown entity_type: {entity_type!r}")

    table = f"schema_registry.{entity_type.lower()}s"
    id_col = f"{entity_type.lower()}_id"
    reason = body.reason if body else "TASK_COMPLETE"

    try:
        result = await db.execute(text(f"""
            UPDATE {table}
            SET status = 'DEAD', died_at = NOW(), death_reason = :reason
            WHERE {id_col} = :eid AND status != 'DEAD'
            RETURNING died_at
        """), {"reason": reason, "eid": entity_id})
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Entity not found or already DEAD.")

        await db.commit()
        logger.info(f"[REGISTRY] Death: {entity_type}/{entity_id} reason={reason}")
        return {"status": "DEAD", "entity_id": entity_id, "died_at": str(row.died_at), "reason": reason}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── List (cursor-based pagination) ──────────────────────────────────────────
@router.get("/list/{entity_type}")
async def entity_list(
    entity_type: str,
    status: str = Query("ACTIVE", description="ACTIVE | DORMANT | DEAD | ALL"),
    limit: int = Query(100, le=1000),
    cursor: str | None = Query(None, description="마지막으로 받은 entity_id (cursor 기반 페이지네이션)"),
    db: AsyncSession = Depends(get_db)
):
    """엔티티 목록 조회 — cursor 기반 페이지네이션 (offset 사용 금지)"""
    et = entity_type.lower()
    if et not in _ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Unknown entity_type: {et!r}")

    table = f"schema_registry.{et}s"
    id_col = f"{et}_id"

    where_clauses = []
    params: dict = {"limit": limit}

    if status.upper() != "ALL":
        where_clauses.append("status = :status")
        params["status"] = status.upper()

    # [Contract #8] cursor 기반 페이지네이션
    if cursor:
        where_clauses.append(f"{id_col} > CAST(:cursor AS uuid)")
        params["cursor"] = cursor

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    try:
        result = await db.execute(text(f"""
            SELECT * FROM {table}
            {where_sql}
            ORDER BY {id_col}
            LIMIT :limit
        """), params)
        rows = [dict(r._mapping) for r in result.fetchall()]
        next_cursor = str(rows[-1][id_col]) if rows else None

        return {
            "entity_type": et,
            "count": len(rows),
            "next_cursor": next_cursor,
            "items": rows
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Materialize (재이식) ─────────────────────────────────────────────────────
@router.post("/materialize/{entity_id}")
async def entity_materialize(entity_id: str, body: MaterializeRequest, db: AsyncSession = Depends(get_db)):
    """BORN_PARTIAL 이후 .doc 파일 이식 재시도"""
    et = body.entity_type.lower()
    if et not in _ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Unknown entity_type: {et!r}")

    # TODO: BirthHookService 구현 후 실제 файл 이식 로직 연결
    logger.info(f"[REGISTRY] Materialize requested: {et}/{entity_id} → {body.instance_path}")
    return {
        "status": "MATERIALIZED",
        "entity_id": entity_id,
        "entity_type": et,
        "instance_path": body.instance_path,
        "note": "BirthHookService integration pending."
    }
