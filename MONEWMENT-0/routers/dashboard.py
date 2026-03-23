from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from core.database import get_db
from core.logger import logger
from datetime import datetime, timedelta
from core.config import settings
from core.constants import SCHEMA_PREFIX

schema_name = f"{SCHEMA_PREFIX}{settings.STRATUM_NAME}"

router = APIRouter(prefix="/v1/dashboard", tags=["Dashboard"])

@router.get("/areum/stats")
async def get_areum_stats(db: AsyncSession = Depends(get_db)):
    """AREUM 전역 학습 현황 통계"""
    try:
        # 1. 원천 데이터 총합 (Stratum 실측 기준)
        res_assets = await db.execute(text(f"SELECT count(*) FROM {schema_name}.assets"))
        total_assets = res_assets.scalar() or 0
        
        # 2. AREUM 추출 데이터 총합
        res_extractions = await db.execute(text(f"SELECT count(*) FROM {schema_name}.assets WHERE ai_summary IS NOT NULL"))
        total_extractions = res_extractions.scalar() or 0
        
        # 3. 오늘 처리량
        res_today = await db.execute(text(f"""
            SELECT count(*) FROM {schema_name}.assets 
            WHERE ai_summary IS NOT NULL AND updated_at > NOW() - INTERVAL '24 hours'
        """))
        today_extractions = res_today.scalar() or 0
        
        # 4. REX 보고서 현황
        res_reports = await db.execute(text("SELECT count(*) FROM schema_rex.areum_reports"))
        total_reports = res_reports.scalar() or 0
        
        return {
            "total_assets": total_assets,
            "total_extractions": total_extractions,
            "today_extractions": today_extractions,
            "total_reports": total_reports,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"[DASHBOARD] Stats query failed: {e}")
        return {"error": str(e)}

@router.get("/metrics")
async def get_dashboard_metrics(db: AsyncSession = Depends(get_db)):
    """[EMPIRE v51.5] Dashboard Data Mapping Protocol 실측 지표"""
    try:
        # A. STRATUM SENT DATA (Raw Archive)
        res_sent = await db.execute(text("SELECT count(*) FROM public.crawl_history"))
        stratum_sent = res_sent.scalar() or 0

        # B. ASSETS STATUS (Refined vs Pending)
        res_refined = await db.execute(text(f"SELECT count(*) FROM {schema_name}.assets WHERE ai_summary IS NOT NULL"))
        assets_refining = res_refined.scalar() or 0
        
        res_pending = await db.execute(text(f"SELECT count(*) FROM {schema_name}.assets WHERE ai_summary IS NULL"))
        assets_pending = res_pending.scalar() or 0

        # C. AREUM TRAINING (AREUM-1 Entity Status)
        res_areum = await db.execute(text("""
            SELECT status, COALESCE(last_seen_at::text, 'NEVER') 
            FROM schema_registry.ants 
            WHERE ant_name = 'AREUM-1' 
            ORDER BY last_seen_at DESC LIMIT 1
        """))
        areum_row = res_areum.fetchone()
        areum_status = areum_row[0] if areum_row else "OFFLINE"
        areum_last_seen = areum_row[1] if areum_row else "N/A"

        # D. REX SUMMARIZING (Cross Reports Queue for this Stratum)
        res_rex = await db.execute(text(f"""
            SELECT count(*) FROM schema_pipeline.cross_reports 
            WHERE stratum_id = (SELECT stratum_id FROM schema_registry.stratums WHERE stratum_name = '{settings.STRATUM_NAME}' LIMIT 1)
        """))
        rex_summarizing = res_rex.scalar() or 0

        return {
            "empire": {
                "stratum_sent": stratum_sent,
                "refining_assets": assets_refining,
                "pending_assets": assets_pending,
                "areum_status": areum_status,
                "rex_queue": rex_summarizing
            },
            "status": "ONLINE",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"[DASHBOARD] Metrics query failed: {e}")
        return {"status": "OFFLINE", "error": str(e)}

@router.get("/areum/recent")
async def get_recent_extractions(db: AsyncSession = Depends(get_db)):
    """최근 AREUM 추출 데이터 샘플 (Join and Labeling)"""
    try:
        # assets 조인 없이 단일 테이블에서 추출 (V51.5 Zero-Mock)
        res = await db.execute(text(f"""
            SELECT areum_id as areum_node_id, 
                   COALESCE(storage_path, hash) as display_source,
                   ai_confidence as confidence_score, 
                   updated_at as extracted_at
            FROM {schema_name}.assets
            WHERE ai_summary IS NOT NULL
            ORDER BY updated_at DESC
            LIMIT 10
        """))
        rows = res.fetchall()
        samples = [
            {
                "node_id": r[0],
                "url": r[1],
                "confidence": r[2],
                "timestamp": r[3].isoformat() if r[3] else None
            } for r in rows
        ]
        return {"samples": samples}
    except Exception as e:
        logger.error(f"[DASHBOARD] Recent samples query failed: {e}")
        return {"samples": [], "error": str(e)}

@router.get("/active_stratums")
async def get_active_stratums(db: AsyncSession = Depends(get_db)):
    """활성화된 영토 리스트"""
    try:
        res = await db.execute(text("SELECT stratum_name, status FROM schema_registry.stratums WHERE status = 'ACTIVE'"))
        rows = res.fetchall()
        return {"stratums": [{"name": r[0], "status": r[1]} for r in rows]}
    except Exception as e:
        return {"stratums": [], "error": str(e)}
