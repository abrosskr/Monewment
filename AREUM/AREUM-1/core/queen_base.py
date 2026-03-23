"""
core/queen_base.py
G4: Physical schema verification in connect() — prevents phantom QUEEN initialization
G5: Remove legacy typing.Optional import
"""
from abc import ABC, abstractmethod
from sqlalchemy import text
from .logger import logger
from .database import engine
from .registry import registry
from .config import settings
import httpx
import json
import gzip


class QueenBase(ABC):
    """모든 Queen이 상속받아야 할 추상 기본 클래스"""

    def __init__(self, stratum_id: str, queen_id: str = "QUEEN-BASE"):
        self.stratum_id = stratum_id
        self.queen_id = queen_id
        if not registry.is_valid(self.stratum_id):
            registry.register_stratum(self.stratum_id, {"status": "ACTIVE", "type": "AUTO_PROVISIONED"})
        self.log_activity("Queen Initialized and Bound to Registry.")

    def log_activity(self, msg: str) -> None:
        logger.info(f"[{self.queen_id}] {msg}")

    async def connect(self) -> bool:
        """
        DB 연결 확인 + [G4] 물리 스키마 존재 여부 검증.
        stratum 스키마가 Supabase 에 실제로 없으면 False 반환.
        """
        self.log_activity("Verifying Database Connection...")
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1;"))

            # [G4 ROUTING GUARD] 물리 스키마가 DB 에 실제로 존재하는지 검증
            # target_schema 를 가진 서브클래스(예: QueenLegacyVendors)는 해당 스키마를 확인
            schema_to_check = getattr(self, "target_schema", None)
            if schema_to_check:
                async with engine.connect() as conn:
                    result = await conn.execute(
                        text("SELECT 1 FROM information_schema.schemata WHERE schema_name = :name"),
                        {"name": schema_to_check}
                    )
                    if not result.fetchone():
                        logger.error(
                            f"[{self.queen_id}] [G4 ROUTING GUARD] "
                            f"Schema '{schema_to_check}' does not exist in Supabase. "
                            f"Run Provisioner.create_stratum_space() first. Aborting Queen."
                        )
                        return False

            self.log_activity("Database Connection and Schema Verified.")
            return True

        except Exception as e:
            logger.error(f"[{self.queen_id}] Database Connection Failed: {e}")
            return False

    async def execute_task(self) -> None:
        pass

    async def self_purge_l1_routine(self) -> int:
        """
        [DECREE 12 / 14] Local Autonomous Purge Routine.
        퀸이 자치적으로 자신의 영토 내에서 REX에 흡수된(rex_consumed=TRUE) 원초 혈류(L1)를 정화하며,
        그 기록을 제국 행정망(data_movements)에 서면 보고합니다.
        """
        # 치안/행정 영토는 스스로 정화하지 않음 (CCTV, GUARD 등이 관리)
        if "SYSTEM" in self.stratum_id.upper() or "REGISTRY" in self.stratum_id.upper():
            return 0
        
        self.log_activity("Initiating Autonomous L1 Purge (Constitutional Compliance).")
        try:
            target_schema = f"schema_stratum_{self.stratum_id}"
            async with engine.begin() as conn:
                # 1. 대상 데이터 정화 (L1 -> Delete)
                query = text(f"""
                    DELETE FROM {target_schema}.assets
                    WHERE rex_consumed = TRUE
                      AND created_at < NOW() - INTERVAL '7 days'
                """)
                result = await conn.execute(query)
                deleted_count = result.rowcount

                # 2. 제국 데이터 이동 장부(data_movements)에 보고
                if deleted_count > 0:
                    audit_query = text("""
                        INSERT INTO schema_registry.data_movements
                        (stratum_id, queen_id, action_type, record_count, reason)
                        VALUES (
                            (SELECT stratum_id FROM schema_registry.stratums WHERE stratum_name = :s_name LIMIT 1),
                            (SELECT queen_id FROM schema_registry.queens WHERE queen_name = :q_name LIMIT 1),
                            'L1_PURGE',
                            :count,
                            :reason
                        )
                    """)
                    await conn.execute(audit_query, {
                        "s_name": self.stratum_id,
                        "q_name": self.queen_id,
                        "count": deleted_count,
                        "reason": f"Lawful autonomous purge of {deleted_count} consumed essence by {self.queen_id}."
                    })
                    self.log_activity(f"L1 Purge Complete: {deleted_count} records extinguished lawfully.")
                else:
                    self.log_activity("L1 Purge Complete: No consumed assets ready for extinguishing.")
                
                return deleted_count

        except Exception as e:
            logger.error(f"[{self.queen_id}] Autonomous L1 Purge Failed: {e}")
            return 0

    async def report_coordinate(self, url: str, file_path: str, hash_val: str, vendor_id: str = None) -> bool:
        """
        [DECREE 12.1] Report Local Coordinate to Core API.
        """
        if not hasattr(self, 'ant_id') or not getattr(self, 'fencing_token', None):
            self.log_activity("[FENCING BLOCK] Coordinate report denied. Only verified ants/queens can report!")
            return False

        try:
            from core.constants import GATEWAY_PORT
            api_url = f"http://127.0.0.1:{GATEWAY_PORT}/v1/pipeline/coordinate"
            headers = {
                "X-Alias": "QUEEN",
                "X-Ant-ID": str(self.ant_id),
                "X-Stratum-ID": str(self.stratum_id),
                "X-Fencing-Token": str(self.fencing_token),
                "Content-Type": "application/json"
            }
            payload = {
                "url": url,
                "file_path": file_path,
                "content_hash": hash_val,
                "vendor_id": vendor_id
            }
            async with httpx.AsyncClient() as client:
                resp = await client.post(api_url, json=payload, headers=headers)
                if resp.status_code not in [201, 200]:
                    logger.error(f"Coordinate API Failed: {resp.status_code} - {resp.text}")
                    return False
            return True
        except Exception as e:
            logger.error(f"report_coordinate Error: {e}")
            return False

    async def pull_local_assets(self):
        """
        [QUEEN-0 OBSERVER] Scan local storage for unreported assets and promote them.
        """
        from pathlib import Path
        import hashlib
        
        self.log_activity("Observing Local Pillar for unreported assets...")
        storage_root = Path("data/raw") / self.stratum_id
        if not storage_root.exists():
            return

        unreported_count = 0
        for date_dir in storage_root.iterdir():
            if not date_dir.is_dir(): continue
            for file in date_dir.glob("*.json"):
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    # Coordinate report (will be ignored if already reported due to hash index)
                    success = await self.report_coordinate(
                        url=data["url"],
                        file_path=str(file.absolute()),
                        hash_val=file.stem
                    )
                    if success: unreported_count += 1
                except Exception as e:
                    logger.error(f"Failed to pull asset {file}: {e}")
        
        if unreported_count > 0:
            self.log_activity(f"Local Observation Complete: {unreported_count} assets synchronized with Core.")

    async def report_asset_with_bypass(self, raw_data: dict, hash_val: str, vendor_id: str) -> bool:
        """
        [LEGACY/HYBRID] Hybrid Storage Bypass + [V40] ANT Delivery Fencing
        """
        if not hasattr(self, 'ant_id') or not getattr(self, 'fencing_token', None):
            self.log_activity("[FENCING BLOCK] Injection denied. Only ANTs can deliver assets!")
            return False

        try:
            data_str = json.dumps(raw_data)
            data_bytes = data_str.encode("utf-8")
            storage_path = None
            
            # Threshold: 10KB
            if len(data_bytes) > 10240 and settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY:
                self.log_activity(f"Data size {len(data_bytes)} bytes > 10KB. Offloading to Storage.")
                storage_path = f"{self.stratum_id}/{hash_val}.json.gz"
                compressed_data = gzip.compress(data_bytes)
                
                upload_url = f"{settings.SUPABASE_URL}/storage/v1/object/{settings.STORAGE_BUCKET_NAME}/{storage_path}"
                headers = {
                    "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
                    "Content-Type": "application/x-gzip",
                    "x-upsert": "true"
                }
                
                async with httpx.AsyncClient() as client:
                    resp = await client.post(upload_url, content=compressed_data, headers=headers)
                    if resp.status_code != 200:
                        logger.error(f"Storage Upload Failed: {resp.text}")
                        return False

            from core.constants import GATEWAY_PORT
            api_url = f"http://127.0.0.1:{GATEWAY_PORT}/v1/pipeline/report"
            headers = {
                "X-Ant-ID": str(self.ant_id),
                "X-Fencing-Token": str(self.fencing_token),
                "Content-Type": "application/json"
            }
            payload = {
                "url": raw_data.get("url", ""),
                "raw_html": raw_data.get("html", ""),
                "cleaned_text": raw_data.get("text", ""),
                "content_hash": hash_val,
                "vendor_id": vendor_id
            }
            async with httpx.AsyncClient() as client:
                api_resp = await client.post(api_url, json=payload, headers=headers)
                if api_resp.status_code != 201:
                    logger.error(f"Delivery API Failed: {api_resp.status_code} - {api_resp.text}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"report_asset_with_bypass Error: {e}")
            return False
