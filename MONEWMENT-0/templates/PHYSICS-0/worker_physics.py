import httpx
import asyncio
import logging
import os
import uuid
import sys
import random
import hashlib
from datetime import datetime
from pathlib import Path

# --- [V51.5 PATH RESOLUTION: DYNAMIC ANCHOR] ---
from core.path_discovery import discover_imperial_anchor, sanitize_and_inject_path
root = discover_imperial_anchor()
if not root:
    # Fallback to absolute parent for safety
    root = Path(__file__).resolve().parent.parent.parent.parent.parent
sanitize_and_inject_path()

if str(root / "MONEWMENT-0") not in sys.path:
    sys.path.insert(0, str(root / "MONEWMENT-0"))

from core.robustness import ImperialGovernance, ensure_alive, get_imperial_client, wait_for_core, retry_ceremony
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- 로깅 ---
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] PHYSICS %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout
)
logger = logging.getLogger("physics.worker")

# --- 설정 ---
class PhysicsSettings(BaseSettings):
    CORE_HOST: str = "127.0.0.1"
    PORT_CORE_API: str = "8800"
    GATEWAY_TOKEN: str = "mon_gw_ch4ng3m3_bef0re_pr0d"
    STRATUM_ID: str = "UNKNOWN"
    QUEEN_ID: str = "UNKNOWN"
    PHYSICS_ID: str = "UNKNOWN"
    PHYSICS_NAME: str = "PHYSICS-1"
    POLL_INTERVAL_SEC: int = 60
    BATCH_SIZE: int = 20
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

cfg = PhysicsSettings()
CORE = f"http://{cfg.CORE_HOST}:{cfg.PORT_CORE_API}/v1"

# ─── [V51.5] GOVERNANCE INITIALIZATION ──────────────────────────────────────
# Using 'ant' instead of 'queen' (Arch Refinement V51.5)
gov = ImperialGovernance(
    entity_type="ant", 
    entity_id=cfg.PHYSICS_ID,
    core_url=CORE,
    gateway_token=cfg.GATEWAY_TOKEN
)

# --- STEP 1: REX 파이프라인에서 미소비 보고서 폴링 ---
@ensure_alive(gov)
async def poll_cross_reports(client: httpx.AsyncClient) -> list[dict]:
    try:
        r = await client.get(
            f"{CORE}/pipeline/cross_reports",
            headers=gov.headers,
            params={"limit": cfg.BATCH_SIZE},
            timeout=10.0
        )
        if r.status_code == 200:
            reports = r.json().get("reports", [])
            if reports:
                logger.info(f"[POLL] {len(reports)}건의 교차 보고서 수집.")
            return reports
        elif r.status_code == 403:
            logger.error("[POLL] ❌ 403 Forbidden: GATEWAY_TOKEN 이 코어 서버와 일치하지 않습니다.")
    except Exception as e:
        logger.warning(f"[POLL] 코어망 연결 실패 (서버가 아직 준비되지 않았을 수 있음): {e}")
    return []

# --- STEP 2: 물리 융합 (Tier 3) ---
@ensure_alive(gov)
async def fuse_intelligence(reports: list[dict]) -> dict:
    """
    [PHASE 8 ALGORITHM] Semantic Fusion.
    여러 영토에서 온 정수(Essence)를 결합하여 전역적인 트렌드 도출.
    """
    logger.info(f"[FUSE] {len(reports)}건의 보고서 융합 분석 중...")
    
    # [V51.5] Simulated Fusion Cost
    gov.current_session_cost += 0.10
    
    combined_keywords = []
    total_confidence = 0.0
    
    for r in reports:
        combined_keywords.extend(r.get("keywords", []))
        total_confidence += r.get("confidence_score", 0.0)
    
    avg_confidence = total_confidence / len(reports) if reports else 0.0
    unique_keywords = list(set(combined_keywords))
    
    return {
        "fusion_type": "CROSS_STRATUM_TREND",
        "involved_stratums": list(set([r.get("stratum_id") for r in reports])),
        "top_keywords": unique_keywords[:10],
        "aggregate_confidence": avg_confidence,
        "summary": f"Fused {len(reports)} reports into a Strategic Decree."
    }

@ensure_alive(gov)
async def push_fusion_decree(client: httpx.AsyncClient, fusion_data: dict, source_ids: list[str]) -> bool:
    try:
        # STEP 3a: Strategic Decree 보고
        r = await client.post(
            f"{CORE}/pipeline/strategic_decrees",
            headers=gov.get_fencing_headers(),
            json={
                "strategic_directive": fusion_data["summary"],
                "focus_sector": "GLOBAL_TREND",
                "correlations": [{"keyword": kw} for kw in fusion_data["top_keywords"]], # list[dict]
                "source_ref_ids": source_ids
            },
            timeout=10.0
        )
        if r.status_code != 201:
            logger.warning(f"[PUSH] Strategic Decree response anomalous: {r.status_code}")
        
        # [V51.5.1] PHYSICAL ANCHORING
        content_json = json.dumps(fusion_data, ensure_ascii=False)
        content_hash = hashlib.md5(content_json.encode()).hexdigest()
        
        data_dir = root / "data" / "physics"
        data_dir.mkdir(parents=True, exist_ok=True)
        storage_path = str(data_dir / f"{content_hash}.json")
        
        with open(storage_path, "w", encoding="utf-8") as f:
            f.write(content_json)
        
        # STEP 3b: Report Intelligence (Physical Anchor Coordinate)
        await client.post(
            f"{CORE}/pipeline/intelligence/reports",
            headers=gov.get_fencing_headers(),
            json={
                "source_id": gov.entity_id,
                "report_type": "PHYSICS_FUSION",
                "payload": {
                    "storage_path": storage_path,
                    "content_hash": content_hash,
                    "stratum_id": cfg.STRATUM_ID,
                    "fusion_type": fusion_data["fusion_type"]
                },
                "stratum_id": cfg.STRATUM_ID
            },
            timeout=10.0
        )
        
        logger.info(f"[PUSH] Strategic Decree anchored to: {storage_path}")
        return True
    except Exception as e:
        logger.error(f"[PUSH] 전략 보고 및 앵커링 실패: {e}")
    return False

import json

@ensure_alive(gov)
async def mark_consumed(client: httpx.AsyncClient, report_ids: list[str]):
    try:
        await client.patch(
            f"{CORE}/pipeline/cross_reports/mark_consumed",
            headers={**gov.get_fencing_headers(), "Idempotency-Key": str(uuid.uuid4())},
            json={"report_ids": report_ids},
            timeout=10.0
        )
    except Exception as e:
        logger.warning(f"[MARK] 소비 마킹 실패: {e}")

# --- 생명주기 루프 ---
async def physics_lifecycle():
    # [FORTIFICATION] Wait for Core API reachability 
    if not await wait_for_core(CORE):
        logger.critical("[SYS] ❌ 코어망 응답 없거나 접속 거부됨. 강제 종료합니다.")
        return

    # [FORTIFICATION] Using Imperial Standardized Client
    async with get_imperial_client(timeout=10.0) as client:
        # 탄생 성사
        idem_key = str(uuid.uuid4())
        logger.info(f"[SYS] 🧬 탄생 성사 시작... (PHYSICS)")
        
        # [V51.5] Unified Birth Ceremony
        idem_key = str(uuid.uuid4())
        logger.info(f"[SYS] [GENE] Birth Ceremony Started... ({cfg.PHYSICS_NAME})")
        
        payload = {
            "ant_name": cfg.PHYSICS_NAME,
            "ant_type": "PHYSICS",
            "queen_id": cfg.QUEEN_ID,
            "stratum_id": cfg.STRATUM_ID,
            "target_url": "LOCAL_PHYSICS_ENGINE"
        }

        try:
            success = await gov.birth(payload, instance_path=str(Path(__file__).resolve().parent), idempotency_key=idem_key)
            if not success:
                raise RuntimeError("Registry Birth Denied.")
            logger.info(f"[SYS] ✅ 탄생 완료 (Entity ID: {gov.entity_id})")
        except Exception as e:
            logger.warning(f"[SYS] 탄생 성사 최종 실패 — 로컬 ID 사용: {e}")

        # [V51.5] Activate Governance Heartbeat
        await gov.start_heartbeat()
        logger.info(f"[SYS] [V51.5] Governance Active for Queen PHYSICS.")

        logger.info(f"[SYS] PHYSICS Engine started (Poll: {cfg.POLL_INTERVAL_SEC}s)")
        
        while gov.is_alive:
            try:
                reports = await poll_cross_reports(client)
                if reports:
                    fusion_result = await fuse_intelligence(reports)
                    report_ids = [r["report_id"] for r in reports]
                    
                    success = await push_fusion_decree(client, fusion_result, report_ids)
                    
                    if success:
                        await mark_consumed(client, report_ids)
                
                await asyncio.sleep(cfg.POLL_INTERVAL_SEC)
            except Exception as e:
                logger.error(f"[LOOP] 알 수 없는 오류: {e}")
                await asyncio.sleep(10)

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(physics_lifecycle())
    except KeyboardInterrupt:
        logger.info("PHYSICS shutdown.")
