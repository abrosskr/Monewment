import json, uuid, asyncio
from typing import List, Optional
from fastapi import APIRouter, Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timedelta, timezone
from core.database import get_db, engine
from core.config import settings
from core.logger import logger
from pydantic import BaseModel

router = APIRouter(prefix="/v1/pipeline", tags=["Pipeline v5.8 [FINAL SYNC]"])

# --- [MODELS] ---
class ConceptRequest(BaseModel):
    babel_id: str
    canonical_name: str
    category: str
    description: Optional[str] = None

class ReportRequest(BaseModel):
    stratum_id: str
    vendor_id: str
    raw_data: str
    storage_path: Optional[str] = None

class IntelligenceReportRequest(BaseModel):
    stratum_id: str
    report_type: str
    content: dict
    confidence_score: float

class AreumAssetUpdate(BaseModel):
    stratum_id: str
    areum_id: str
    ai_summary: str
    essence_tags: list[str]
    ai_confidence: float

class KnowledgeTripleRequest(BaseModel):
    subject_id: str
    predicate: str
    object_id: str
    confidence_score: float = 1.0
    source_queen_id: Optional[str] = None

class StrategicDecreeRequest(BaseModel):
    stratum_id: str
    strategic_directive: str
    focus_sector: str | None = None
    correlations: list | None = []

# --- [INFRA GUARD] ---
async def enforce_database_schema():
    async with engine.begin() as conn:
        try:
            logger.info("[INFRA-GUARD] Executing physical schema verification...")
            await conn.execute(text("""
                DO $$ BEGIN 
                    -- [V5.8] Strategic Decrees 테이블 물리 보정 (PHASE 34.0)
                    BEGIN ALTER TABLE schema_pipeline.strategic_decrees ADD COLUMN stratum_id UUID; EXCEPTION WHEN duplicate_column THEN NULL; END;
                    BEGIN ALTER TABLE schema_pipeline.strategic_decrees ADD COLUMN rex_consumed BOOLEAN DEFAULT FALSE; EXCEPTION WHEN duplicate_column THEN NULL; END;
                    BEGIN ALTER TABLE schema_pipeline.strategic_decrees ADD COLUMN rex_consumed_at TIMESTAMP; EXCEPTION WHEN duplicate_column THEN NULL; END;
                    
                    -- [V10.0] Cross Reports 구조 보정
                    BEGIN ALTER TABLE schema_pipeline.cross_reports ADD COLUMN report_type TEXT; EXCEPTION WHEN duplicate_column THEN NULL; END;
                    BEGIN ALTER TABLE schema_pipeline.cross_reports ADD COLUMN confidence_score FLOAT; EXCEPTION WHEN duplicate_column THEN NULL; END;
                    BEGIN ALTER TABLE schema_pipeline.cross_reports ADD COLUMN raw_essence JSONB; EXCEPTION WHEN duplicate_column THEN NULL; END;
                    
                    -- [V11.0] Babel Knowledge Triples Autonomous Genesis
                    CREATE TABLE IF NOT EXISTS schema_babel.knowledge_triples (
                        triple_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        subject_id TEXT NOT NULL,
                        predicate TEXT NOT NULL,
                        object_id TEXT NOT NULL,
                        confidence_score DOUBLE PRECISION DEFAULT 1.0,
                        source_queen_id UUID,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    );
                    -- [External Reference]
                    BEGIN ALTER TABLE schema_babel.concepts ADD COLUMN external_ref_id TEXT; EXCEPTION WHEN duplicate_column THEN NULL; END;
                END $$;
            """))
            logger.info("[INFRA-GUARD] Synchronization Success.")
        except Exception as e:
            logger.error(f"[INFRA-GUARD] CRITICAL SCHEMA SYNC FAILURE: {e}")

# --- [HELPERS] ---
async def get_schema_name(stratum_id: str, db: AsyncSession) -> str:
    # [EMERGENCY REPAIR] Hardcoded Safety for STRATUM-1
    if stratum_id == "badd8a15-5e63-4d24-81fd-489e8973cb85":
        return "schema_stratum_STRATUM-1"
    try:
        q = text("SELECT stratum_name FROM schema_registry.stratums WHERE stratum_id::text = :sid")
        res = await db.execute(q, {"sid": stratum_id})
        row = res.fetchone()
        return f"schema_stratum_{row[0]}" if row else "schema_stratum_STRATUM-1"
    except Exception:
        return "schema_stratum_STRATUM-1"

async def verify_token(x_queen_token: str = Header(..., alias="X-Queen-Token")):
    if x_queen_token != settings.GATEWAY_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid Gateway Token")

# --- [ROUTES] ---

@router.post("/report", dependencies=[Depends(verify_token)])
async def post_raw_report(req: ReportRequest, db: AsyncSession = Depends(get_db)):
    """[V1.0] 원천 데이터 보고 (The Foundation)"""
    try:
        schema_name = await get_schema_name(req.stratum_id, db)
        q = text(f"""
            INSERT INTO "{schema_name}".assets (storage_path, raw_data, pipeline_state)
            VALUES (:path, :data, 'RAW_DUMPED')
            RETURNING id
        """)
        res = await db.execute(q, {"path": req.storage_path, "data": req.raw_data})
        await db.commit()
        return {"status": "INJECTED", "asset_id": str(res.fetchone()[0])}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assets/pending", dependencies=[Depends(verify_token)])
async def get_pending_assets(stratum_id: str, limit: int = 20, db: AsyncSession = Depends(get_db)):
    try:
        schema_name = await get_schema_name(stratum_id, db)
        q = text(f'SELECT id::text, storage_path, raw_data FROM "{schema_name}".assets WHERE ai_summary IS NULL LIMIT :limit')
        res = await db.execute(q, {"limit": limit})
        return {"stratum_id": stratum_id, "assets": [dict(r._mapping) for r in res.fetchall()]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning/pending", dependencies=[Depends(verify_token)])
async def get_pending_learning(limit: int = 10, db: AsyncSession = Depends(get_db)):
    """[REX 학습 대기열] REX Type Hardening (stratum_id::text)"""
    try:
        q = text("""
            SELECT decree_id::text, stratum_id::text, strategic_directive, focus_sector, correlations, created_at
            FROM schema_pipeline.strategic_decrees
            WHERE rex_consumed = FALSE
            ORDER BY created_at ASC LIMIT :limit
        """)
        res = await db.execute(q, {"limit": limit})
        return {"decrees": [dict(r._mapping) for r in res.fetchall()]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/strategic_decrees", dependencies=[Depends(verify_token)])
async def post_strategic_decree(req: StrategicDecreeRequest, db: AsyncSession = Depends(get_db)):
    """[PHASE 33.0] 전술 지시 하달"""
    try:
        correlations_json = json.dumps(req.correlations, ensure_ascii=False)
        q = text("""
            INSERT INTO schema_pipeline.strategic_decrees 
            (strategic_directive, focus_sector, correlations, stratum_id, rex_consumed)
            VALUES (:directive, :sector, CAST(:correlations AS JSONB), CAST(:sid AS uuid), FALSE)
            RETURNING decree_id
        """)
        res = await db.execute(q, {
            "directive": req.strategic_directive, "sector": req.focus_sector,
            "correlations": correlations_json, "sid": req.stratum_id
        })
        await db.commit()
        return {"status": "DECREED", "decree_id": str(res.fetchone()[0])}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/strategic_decrees/mark_consumed", dependencies=[Depends(verify_token)])
async def mark_decrees_consumed(decree_ids: List[str], db: AsyncSession = Depends(get_db)):
    """[TEMPORAL PURGE] REX 학습 완료 마킹 - Naive KST 강제 주입"""
    try:
        from datetime import datetime, timedelta, timezone
        # [TEMPORAL CONSTITUTION] DB 엔진의 자동 UTC 차감을 막기 위해 Naive KST 주입
        now_kst = datetime.now(timezone(timedelta(hours=9))).replace(tzinfo=None)
        q = text("""
            UPDATE schema_pipeline.strategic_decrees
            SET rex_consumed = TRUE, rex_consumed_at = :now
            WHERE decree_id::text = ANY(:ids)
        """)
        await db.execute(q, {"ids": decree_ids, "now": now_kst})
        await db.commit()
        return {"status": "CONSUMED", "count": len(decree_ids)}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/cross_reports/mark_consumed", dependencies=[Depends(verify_token)])
async def alias_mark_consumed(report_ids: List[str], db: AsyncSession = Depends(get_db)):
    """[Route Aliasing] PHYSICS/REX 워커 호환용 별칭"""
    return await mark_decrees_consumed(report_ids, db)

@router.patch("/assets/{asset_id}/areum", dependencies=[Depends(verify_token)])
async def patch_asset_areum(asset_id: str, req: AreumAssetUpdate, db: AsyncSession = Depends(get_db)):
    """[AREUM 정제 결과 업데이트]"""
    try:
        schema_name = await get_schema_name(req.stratum_id, db)
        q = text(f"""
            UPDATE "{schema_name}".assets
            SET ai_summary = :summary, essence_tags = :tags, ai_confidence = :confidence,
                areum_id = :areum_id, areum_processed_at = :now, pipeline_state = 'AREUM_DONE'
            WHERE id::text = :asset_id
        """)
        await db.execute(q, {
            "summary": req.ai_summary, 
            "tags": json.dumps(req.essence_tags), 
            "confidence": req.ai_confidence, 
            "areum_id": req.areum_id, 
            "asset_id": asset_id,
            "now": datetime.now(timezone(timedelta(hours=9))).replace(tzinfo=None)
        })
        await db.commit()
        return {"status": "MUTATED", "asset_id": asset_id}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/intelligence/reports", dependencies=[Depends(verify_token)])
async def post_intelligence_report(req: IntelligenceReportRequest, db: AsyncSession = Depends(get_db)):
    """[지능 보고서 수집/송신]"""
    try:
        content_json = json.dumps(req.content, ensure_ascii=False)
        q = text("""
            INSERT INTO schema_pipeline.cross_reports (stratum_id, report_type, summary, confidence_score, raw_essence)
            VALUES (CAST(:sid AS uuid), :type, :summary, :score, CAST(:content AS JSONB))
            RETURNING report_id
        """)
        res = await db.execute(q, {
            "sid": req.stratum_id, 
            "type": req.report_type, 
            "summary": req.content.get("summary", "No summary"), 
            "score": req.confidence_score, 
            "content": content_json
        })
        await db.commit()
        return {"status": "REPORTED", "report_id": str(res.fetchone()[0])}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/intelligence/reports", dependencies=[Depends(verify_token)])
async def get_intelligence_reports(limit: int = 20, db: AsyncSession = Depends(get_db)):
    try:
        q = text("SELECT report_id::text, stratum_id, report_type, summary, confidence_score, raw_essence FROM schema_pipeline.cross_reports ORDER BY created_at DESC LIMIT :limit")
        res = await db.execute(q, {"limit": limit})
        return {"status": "SUCCESS", "reports": [dict(r._mapping) for r in res.fetchall()]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/knowledge/concepts", dependencies=[Depends(verify_token)])
async def post_knowledge_concepts(concepts: list[ConceptRequest], db: AsyncSession = Depends(get_db)):
    """[SOVEREIGN SEEDING] 온톨로지 등록"""
    try:
        q = text("""
            INSERT INTO schema_babel.concepts (babel_id, canonical_name, category, description)
            VALUES (:id, :name, :cat, :desc)
            ON CONFLICT (babel_id) DO UPDATE SET 
                canonical_name = EXCLUDED.canonical_name,
                category = EXCLUDED.category,
                description = EXCLUDED.description
        """)
        for c in concepts:
            await db.execute(q, {"id": c.babel_id, "name": c.canonical_name, "cat": c.category, "desc": c.description})
        await db.commit()
        return {"status": "ONTOLOGY_REGISTERED", "count": len(concepts)}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/knowledge/inscribe", dependencies=[Depends(verify_token)])
async def post_knowledge_inscribe(triples: list[KnowledgeTripleRequest], db: AsyncSession = Depends(get_db)):
    """[V9.0 COMMAND-PROTOCOL] 지능 각인 전용"""
    try:
        q = text("""
            INSERT INTO schema_babel.knowledge_triples 
            (subject_id, predicate, object_id, confidence_score, source_queen_id)
            VALUES (:sub, :pred, :obj, :score, CAST(:q_id AS uuid))
            ON CONFLICT DO NOTHING
        """)
        for t in triples:
            if not t.source_queen_id:
                raise HTTPException(status_code=400, detail="Queen Seal Required")
            await db.execute(q, {
                "sub": t.subject_id, "pred": t.predicate, "obj": t.object_id,
                "score": t.confidence_score, "q_id": t.source_queen_id
            })
        await db.commit()
        return {"status": "COMMAND_ACCEPTED", "count": len(triples)}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/knowledge/triples", dependencies=[Depends(verify_token)])
async def post_knowledge_triples(triples: list[KnowledgeTripleRequest], db: AsyncSession = Depends(get_db)):
    """[BABEL] 지식 트리플 적재 (Legacy Compat)"""
    return await post_knowledge_inscribe(triples, db)