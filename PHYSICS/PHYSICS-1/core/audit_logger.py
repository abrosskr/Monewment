import sys
import datetime
import uuid
import json
from pathlib import Path

# [DECREE 13] Path alignment for MONEWMENT-0 Core
root = Path(__file__).resolve().parent.parent.parent
if str(root / "MONEWMENT-0") not in sys.path:
    sys.path.insert(0, str(root / "MONEWMENT-0"))

from sqlalchemy import text
from core.database import engine
from core.logger import logger

class AuditLogger:
    """[DECREE 13] 데이터 변동 이력(Traceability)을 기록하는 통합 감사 모듈"""
    
    @staticmethod
    async def log_movement(
        action_type: str,
        source: str,
        target: str = "NULL",
        count: int = 0,
        reason: str = "Unspecified",
        sample_data: dict = None
    ):
        """데이터 이동 또는 삭제 이력을 DB에 기록 (없으면 schema_registry 생성)"""
        record_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        
        log_entry = {
            "id": record_id,
            "timestamp": timestamp.isoformat(),
            "action": action_type,
            "source": source,
            "target": target,
            "count": count,
            "reason": reason,
            "sample_hash": hash(str(sample_data)) if sample_data else 0
        }
        
        # 1. 로컬 파일 시스템에 안전하게 기록 (DB 장애 대비 - Zero-Entropy)
        log_dir = Path("c:/monewment/MONEWMENT-0/logs/audit")
        log_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(log_dir / f"{timestamp.date().isoformat()}_audit.log", "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"[AUDIT FAIL] Local file write failed: {e}")
            
        # 2. 전사 레지스트리에 기록 시도
        try:
            async with engine.begin() as conn:
                await conn.execute(text("""
                    INSERT INTO schema_registry.data_movements 
                    (id, timestamp, action_type, source_location, target_location, record_count, reason, sample_hash)
                    VALUES (:id, :ts, :action, :src, :tgt, :cnt, :reason, :hash)
                """), {
                    "id": record_id,
                    "ts": timestamp,
                    "action": action_type,
                    "src": source,
                    "tgt": target,
                    "cnt": count,
                    "reason": reason,
                    "hash": str(hash(str(sample_data))) if sample_data else "0"
                })
        except Exception as e:
            logger.error(f"[AUDIT FAIL] Failed to log movement to DB: {e}")

    @staticmethod
    def log_critical_deletion(target: str, reason: str):
        """[ALERT] 중대한 데이터 삭제 발생 시 즉시 로깅"""
        logger.warning(f"🚨 [CRITICAL DELETE] Target: {target} | Reason: {reason}")
        # Note: 인스턴트 로깅은 비차단식(logger.warning)으로 수행하여 성능 영향 최소화
