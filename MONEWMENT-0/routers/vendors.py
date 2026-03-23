from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.logger import logger
from routers.pipeline import get_schema_name
from types import SimpleNamespace

router = APIRouter(prefix="/vendors", tags=["Vendors"])

@router.get("/")
async def list_vendors(db: AsyncSession = Depends(get_db)):
    """[STRATUM-1] 등록된 모든 벤더(Vendor) 목록 조회"""
    try:
        # 물리적 스키마에 직접 접근하여 데이터 조회
        query = text("SELECT * FROM schema_stratum_vendors.vendors ORDER BY name ASC")
        result = await db.execute(query)
        # SQLAlchemy Row 객체를 dict로 변환
        vendors = [dict(row._mapping) for row in result]
        
        logger.info(f"API: Fetched {len(vendors)} vendors from Stratum-1")
        return {"count": len(vendors), "data": vendors}
    except Exception as e:
        logger.error(f"API Error (list_vendors): {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Observation Error")

from pydantic import BaseModel
from fastapi import Header

class AssetDeliveryRequest(BaseModel):
    hash: str
    raw_data: str | None = None
    storage_path: str | None = None
    pipeline_state: str | None = "RAW_DUMPED" # [V51.5]
    accumulated_cost: float | None = 0.0     # [V51.5]

@router.post("/{stratum_id}/{vendor_id}/assets", status_code=201)
async def deliver_asset(
    stratum_id: str,
    vendor_id: str,
    body: AssetDeliveryRequest,
    x_ant_id: str = Header(..., alias="X-Ant-ID"),
    x_fencing_token: int = Header(..., alias="X-Fencing-Token"),
    db: AsyncSession = Depends(get_db)
):
    """[V40 Delivery Fencing] 오직 합법적인 ANT만이 데이터(Asset)를 배달할 수 있음."""
    # 1. ANT/QUEEN Registry & Fencing Token 검증
    # [V51.5 Fix] Queen도 직접 보고할 수 있도록 ants와 queens 테이블을 모두 조회
    # [V51.5 Defense] QUEEN-OVERRIDE 같은 특수 ID 예외 처리 (UUID 캐스팅 방지)
    if x_ant_id == "QUEEN-OVERRIDE":
         logger.info("[FENCING GUARD] QUEEN-OVERRIDE detected. Bypassing strict registry check.")
         entity_row = SimpleNamespace(status='ACTIVE', fencing_token=x_fencing_token)
    else:
        try:
            entity_check = await db.execute(text("""
                SELECT status, fencing_token FROM (
                    SELECT status, fencing_token, ant_id as id FROM schema_registry.ants
                    UNION ALL
                    SELECT status, fencing_token, queen_id as id FROM schema_registry.queens
                ) AS combined_registry
                WHERE id = CAST(:eid AS uuid)
            """), {"eid": x_ant_id})
            entity_row = entity_check.fetchone()
        except Exception as e:
            logger.error(f"[FENCING GUARD] ID Format error or Registry query failed: {e}")
            raise HTTPException(status_code=400, detail="Invalid Identity Format.")

    if not entity_row:
        logger.warning(f"[FENCING GUARD] Unknown Entity {x_ant_id} attempted delivery.")
        raise HTTPException(status_code=403, detail="Forbidden: Unknown Entity.")
    
    if entity_row.status not in ('ACTIVE', 'RUNNING'):
        logger.warning(f"[FENCING GUARD] Inactive Entity {x_ant_id} (Status: {entity_row.status}) attempted delivery.")
        raise HTTPException(status_code=403, detail=f"Forbidden: Entity is not ACTIVE (Current: {entity_row.status}).")
        
    if entity_row.fencing_token != x_fencing_token:
        # Fencing token mismatch is critical for both ANTs and Queens
        logger.warning(f"[FENCING GUARD] Stale token from Entity {x_ant_id} (Provided: {x_fencing_token}, Expected: {entity_row.fencing_token}).")
        raise HTTPException(status_code=403, detail="Forbidden: Stale fencing token. Please ping registry.")

    # 2. 하역 (DB Insert)
    # [V51.5 Fix] "None" 문자열로 들어오는 경우 NULL로 처리
    real_vendor_id = vendor_id if (vendor_id and isinstance(vendor_id, str) and vendor_id.lower() != "none") else None
    
    try:
        # [수정] 정확한 스키마 이름 풀이 (UUID -> 논리 명칭 기반 스키마)
        stratum_schema = await get_schema_name(stratum_id, db)
        
        if body.storage_path:
            query = text(f"""
                INSERT INTO {stratum_schema}.assets 
                (vendor_id, storage_path, hash, pipeline_state, accumulated_cost) 
                VALUES (:v_id, :s_path, :hash, :p_state, :a_cost)
                ON CONFLICT (hash) DO UPDATE 
                SET pipeline_state = EXCLUDED.pipeline_state,
                    accumulated_cost = assets.accumulated_cost + EXCLUDED.accumulated_cost
            """)
            await db.execute(query, {
                "v_id": real_vendor_id, 
                "s_path": body.storage_path, 
                "hash": body.hash,
                "p_state": body.pipeline_state,
                "a_cost": body.accumulated_cost or 0.0
            })
        else:
            query = text(f"""
                INSERT INTO {stratum_schema}.assets 
                (vendor_id, raw_data, hash, pipeline_state, accumulated_cost) 
                VALUES (:v_id, :raw, :hash, :p_state, :a_cost)
                ON CONFLICT (hash) DO UPDATE 
                SET pipeline_state = EXCLUDED.pipeline_state,
                    accumulated_cost = assets.accumulated_cost + EXCLUDED.accumulated_cost
            """)
            await db.execute(query, {
                "v_id": real_vendor_id, 
                "raw": body.raw_data, 
                "hash": body.hash,
                "p_state": body.pipeline_state,
                "a_cost": body.accumulated_cost or 0.0
            })
        
        await db.commit()
        logger.info(f"[DELIVERY] ANT {x_ant_id} successfully delivered asset to stratum {stratum_id}")
        return {"status": "DELIVERED", "hash": body.hash}
    except Exception as e:
        logger.error(f"[DELIVERY ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delivery failed: {str(e)}")

@router.post("/{vendor_name}/crawl")
async def trigger_crawl(vendor_name: str):
    """(Stub) 특정 벤더 크롤링 명령 트리거"""
    logger.info(f"API: Received crawl command for {vendor_name}")
    return {"status": "queued", "target": vendor_name, "message": "Ant dispatched (Simulation)"}
