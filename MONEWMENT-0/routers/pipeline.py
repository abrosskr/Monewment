"""
routers/pipeline.py ── AREUM ── REX 파이프라인 API 라우터
API Contract v2.0 / Iron Triangle
"""
import uuid
import hashlib
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
import json
import time
import re
import traceback

from core.database import get_db, engine
from core.config import settings
from core.logger import logger

router = APIRouter(prefix="/v1/pipeline", tags=["Pipeline (AREUM/REX)"])

# ─── UTILITIES ───
_schema_cache = {}

async def get_schema_name(stratum_id: str, db: AsyncSession) -> str:
    now = time.time()
    if stratum_id in _schema_cache:
        cached_schema, expires_at = _schema_cache[stratum_id]
        if now < expires_at:
            return cached_schema
    try:
        if not re.match(r'^[a-fA-F0-9-]{36}$', stratum_id):
            return f"schema_stratum_{stratum_id}"

        # [DNA-DIRECTIVE] Use text comparison to break uuid/text mismatch deadlock
        query = text("SELECT stratum_name FROM schema_registry.stratums WHERE stratum_id::text = :sid")
        result = await db.execute(query, {"sid": stratum_id})
        row = result.fetchone()
        
        if not row:
            return f"schema_stratum_{stratum_id}"
            
        stratum_name = row[0]
        schema_name = f"schema_stratum_{stratum_name}"
        _schema_cache[stratum_id] = (schema_name, now + 3600)
        return schema_name
    except Exception as e:
        await db.rollback() 
        logger.error(f"[PIPELINE-DNA] Schema resolution failed: {e}")
        return f"schema_stratum_{stratum_id}"

# ─── FENCING SYSTEM ───
async def verify_fencing(db: AsyncSession, entity_type: str, entity_id: str, fencing_token: int):
    query = text(f"SELECT fencing_token FROM schema_registry.{entity_type}s WHERE {entity_type}_id = :eid")
    try:
        res = await db.execute(query, {"eid": entity_id})
        row = res.fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Entity NOT in Registry")
        if fencing_token < row[0]:
            raise HTTPException(status_code=409, detail="Zombie Process Blocked")
        return True
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[PIPELINE-DNA] Fencing check failed: {e}")
        await db.rollback() 
        raise HTTPException(status_code=500, detail="Fencing Protocol Failure")

async def verify_token(x_queen_token: str = Header(...)):
    if x_queen_token != settings.GATEWAY_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid Gateway Token")

class RawReportRequest(BaseModel):
    url: str
    raw_html: str
    cleaned_text: str
    content_hash: str
    vendor_id: Optional[str] = None

# ─── ENDPOINTS ───

@router.post("/report", status_code=201, dependencies=[Depends(verify_token)])
async def report_raw_asset(
    payload: RawReportRequest,
    db: AsyncSession = Depends(get_db),
    x_fencing_token: str = Header(..., alias="X-Fencing-Token"),
    x_ant_id: str = Header(..., alias="X-Ant-ID"),
    x_alias: str = Header(..., alias="X-Alias"),
    x_stratum_id: str = Header(..., alias="X-Stratum-ID")
):
    """[V51.5 FINAL RECTIFICATION] Direct DB Injection (Surgery)"""
    # 1. Fencing
    entity_type = "queen" if x_alias.upper() == "QUEEN" else "ant"
    await verify_fencing(db, entity_type, x_ant_id, int(x_fencing_token))

    # 2. Schema
    schema_name = await get_schema_name(x_stratum_id, db)

    # 3. Direct Ingestion (Surgery - Pure Typed parameters)
    from uuid import UUID
    try:
        vid_obj = UUID(payload.vendor_id) if payload.vendor_id else None
    except Exception:
        vid_obj = None

    data_json = {"url": payload.url, "html": payload.raw_html, "text": payload.cleaned_text}
    
    # Using explicit CASTs for the final surgery to satisfy the registry trigger
    query = text(f"""
        INSERT INTO "{schema_name}".assets (raw_data, hash, pipeline_state, vendor_id) 
        VALUES (CAST(:data AS JSONB), :hash, 'RAW_DUMPED', CAST(:vid AS UUID))
        ON CONFLICT (hash) DO NOTHING
    """)
    
    try:
        await db.execute(query, {
            "data": json.dumps(data_json),
            "hash": payload.content_hash,
            "vid": str(vid_obj) if vid_obj else None
        })
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"[PIPELINE-DNA] Direct Injection FAILED into {schema_name}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Constitutional Ingestion Failed.")

    return {"status": "reported", "hash": payload.content_hash}

@router.get("/assets/pending", dependencies=[Depends(verify_token)])
async def get_pending_assets(
    stratum_id: str = Query(..., description="소속 영토 UUID"),
    db: AsyncSession = Depends(get_db)
):
    schema_name = await get_schema_name(stratum_id, db)
    result = await db.execute(text(f"SELECT id::text FROM \"{schema_name}\".assets WHERE ai_summary IS NULL LIMIT 20"))
    return {"assets": [dict(r._mapping) for r in result.fetchall()]}
