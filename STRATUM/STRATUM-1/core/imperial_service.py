"""
core/imperial_service.py
제국 자율 행정망(STRATUM-SYSTEM) 관제관: QUEEN-IN-IMPERIAL 및 황실 공무원 ANT
헌법에 의거하여 크로스 스트라텀(Cross-Stratum) 데이터 삭제를 금지하며, 관측 및 기록(Read-only)의 의무만 수행
"""
import asyncio
from sqlalchemy import text
from core.database import engine
from core.logger import logger
from core.robustness import ImperialGovernance
from core.config import settings
from core.constants import GATEWAY_PORT

class QueenImperial:
    def __init__(self):
        self.queen_id = "QUEEN-IN-IMPERIAL"
        self.stratum_id = "SYSTEM"
        self.core_url = f"http://127.0.0.1:{GATEWAY_PORT}/v1"
        self.token = settings.GATEWAY_TOKEN

        # [V51.5 GOVERNANCE] Initialize Governance for each Civil Servant ANT
        self.cctv_gov = ImperialGovernance("ANT", "ANT-CODE-CCTV", self.core_url, self.token)
        self.guard_gov = ImperialGovernance("ANT", "ANT-CODE-GUARD", self.core_url, self.token)
        self.orch_gov = ImperialGovernance("ANT", "ANT-CODE-ORCHESTRA", self.core_url, self.token)

    async def run_cctv_ant(self):
        """
        ANT-CODE-CCTV: 생태계 이상 징후(Dormant Entities) 관측
        """
        # [GOVERNANCE] Birth & Heartbeat
        await self.cctv_gov.birth(
            payload={"ant_name": "ANT-CODE-CCTV", "queen_id": self.queen_id, "ant_type": "CODE"},
            instance_path="core.imperial_service.run_cctv_ant"
        )
        await self.cctv_gov.start_heartbeat()

        logger.info(f"[{self.queen_id}] ANT-CODE-CCTV deployed to monitoring post.")
        while True:
            try:
                async with engine.connect() as conn:
                    # 24시간 이상 방치된 Queen 탐지
                    result = await conn.execute(text("""
                        SELECT queen_id, queen_name, last_seen_at
                        FROM schema_registry.queens
                        WHERE last_seen_at < NOW() - INTERVAL '24 hours'
                          AND status = 'ACTIVE'
                    """))
                    dormant_queens = result.fetchall()
                    if dormant_queens:
                        for dq in dormant_queens:
                            logger.warning(f"[{self.queen_id}] [CCTV-ANT] Dormant Queen detected: {dq.queen_name} (Last seen: {dq.last_seen_at}). Recommend Quarantine.")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[{self.queen_id}] CCTV-ANT Error: {e}")
            await asyncio.sleep(3600)  # 1시간 주기로 스캔

    async def run_guard_ant(self):
        """
        ANT-CODE-GUARD: 시스템 무결성(Integrity) 검열
        """
        # [GOVERNANCE] Birth & Heartbeat
        await self.guard_gov.birth(
            payload={"ant_name": "ANT-CODE-GUARD", "queen_id": self.queen_id, "ant_type": "CODE"},
            instance_path="core.imperial_service.run_guard_ant"
        )
        await self.guard_gov.start_heartbeat()

        logger.info(f"[{self.queen_id}] ANT-CODE-GUARD deployed to patrol.")
        while True:
            try:
                async with engine.connect() as conn:
                    # 72시간 지난 Idempotency Key 검열
                    result = await conn.execute(text("""
                        SELECT COUNT(*)
                        FROM schema_registry.idempotency_keys
                        WHERE created_at < NOW() - INTERVAL '72 hours'
                    """))
                    stale_count = result.scalar()
                    if stale_count and stale_count > 0:
                        logger.warning(f"[{self.queen_id}] [GUARD-ANT] {stale_count} stale idempotency keys found. Master Decree recommended for cleanup.")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[{self.queen_id}] GUARD-ANT Error: {e}")
            await asyncio.sleep(43200)  # 12시간 주기

    async def run_orchestra_ant(self):
        """
        [V43] ANT-CODE-ORCHESTRA: REX 학습 스케줄러 및 부하 조율사
        """
        # [GOVERNANCE] Birth & Heartbeat
        await self.orch_gov.birth(
            payload={"ant_name": "ANT-CODE-ORCHESTRA", "queen_id": self.queen_id, "ant_type": "CODE"},
            instance_path="core.imperial_service.run_orchestra_ant"
        )
        await self.orch_gov.start_heartbeat()

        logger.info(f"[{self.queen_id}] ANT-CODE-ORCHESTRA deployed to manage REX learning queue.")
        while True:
            try:
                # 1. PENDING 보고서 수집 및 QUEUE 적재를 하나의 트랜잭션으로 처리
                async with engine.begin() as conn:
                    result = await conn.execute(text("""
                        SELECT report_id, report_type
                        FROM schema_rex.areum_reports
                        WHERE processing_status = 'PENDING'
                        ORDER BY received_at ASC LIMIT 10
                    """))
                    pending_reports = result.fetchall()
                    
                    if pending_reports:
                        logger.info(f"[{self.queen_id}] [ORCHESTRA-ANT] Found {len(pending_reports)} PENDING AREUM reports. Orchestrating...")
                        
                        for r in pending_reports:
                            await conn.execute(text("""
                                INSERT INTO schema_rex.learning_queue (report_id, target_model, status, orchestrator_id)
                                VALUES (:r_id, 'llama3', 'QUEUED', :orc_id)
                            """), {"r_id": r.report_id, "orc_id": "ANT-CODE-ORCHESTRA"})
                            
                            await conn.execute(text("""
                                UPDATE schema_rex.areum_reports SET processing_status = 'QUEUED' WHERE report_id = :r_id
                            """), {"r_id": r.report_id})
                            
                # 2. REX 엔진 타격 (트랜잭션 외부에서 수행)
                if 'pending_reports' in locals() and pending_reports:
                    import httpx
                    try:
                        async with httpx.AsyncClient() as client:
                            res = await client.post("http://127.0.0.1:8810/v1/rex/train/trigger", timeout=5.0)
                            if res.status_code == 200:
                                logger.info(f"[{self.queen_id}] [ORCHESTRA-ANT] Successfully dispatched QUEUED commands to REX.")
                    except Exception as e:
                        logger.warning(f"[{self.queen_id}] [ORCHESTRA-ANT] REX core unreachable or busy: {e}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[{self.queen_id}] ORCHESTRA-ANT Error: {e}")
            await asyncio.sleep(30)  # 30초 단위 초미세 스캔


queen_imperial = QueenImperial()
