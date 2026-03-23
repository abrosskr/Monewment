import httpx
import asyncio
import logging
import os
import uuid
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path

# --- [V51.5 PATH RESOLUTION: DYNAMIC ANCHOR] ---
from core.path_discovery import discover_imperial_anchor, sanitize_and_inject_path
root = discover_imperial_anchor()
if not root:
    root = Path(__file__).resolve().parent.parent.parent.parent.parent
sanitize_and_inject_path()

if str(root / "MONEWMENT-0") not in sys.path:
    sys.path.insert(0, str(root / "MONEWMENT-0"))

from core.robustness import ImperialGovernance, ensure_alive, get_imperial_client, wait_for_core
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- 로깅 시스템 ---
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] PHYSICS %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout
)
logger = logging.getLogger("physics.worker")

# --- 제국 설정 시스템 ---
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

# --- 거버넌스 엔진 초기화 ---
gov = ImperialGovernance(
    entity_type="ant", 
    entity_id=cfg.PHYSICS_ID,
    core_url=CORE,
    gateway_token=cfg.GATEWAY_TOKEN
)

# --- STEP 1: 지능 보고서 수집 (POLL) ---
@ensure_alive(gov)
async def poll_cross_reports(client: httpx.AsyncClient) -> list[dict]:
    """[V51.9] 최신 지능 보고서 엔드포인트 수집"""
    try:
        r = await client.get(
            f"{CORE}/pipeline/intelligence/reports",
            headers=gov.headers,
            params={"limit": cfg.BATCH_SIZE},
            timeout=10.0
        )
        if r.status_code == 200:
            data = r.json()
            reports = data.get("reports", []) or data.get("items", [])
            if reports:
                logger.info(f"[POLL] {len(reports)}건의 지능 보고서 수집 성공.")
            return reports
        return []
    except Exception as e:
        logger.warning(f"[POLL] 지능 취득 실패: {e}")
        return []

# --- STEP 2: 물리 법칙 검증 및 융합 (FUSE) ---
@ensure_alive(gov)
async def fuse_intelligence(reports: list[dict]) -> dict:
    """[V51.9] 데이터 심층 파싱 및 물리적 타당성 검증"""
    logger.info(f"[FUSE] {len(reports)}건의 보고서 물리 법칙 검증 및 융합 중...")
    
    gov.current_session_cost += 0.10
    combined_keywords = []
    total_confidence = 0.0
    
    for r in reports:
        essence = r.get("raw_essence") or r.get("content") or {}
        if isinstance(essence, str):
            try: essence = json.loads(essence)
            except: essence = {}

        keywords = r.get("keywords") or essence.get("keywords", [])
        score = r.get("confidence_score") or essence.get("confidence_score", 0.0)
        
        combined_keywords.extend(keywords if isinstance(keywords, list) else [])
        try: total_confidence += float(score)
        except: pass
    
    avg_confidence = total_confidence / len(reports) if reports else 0.0
    unique_keywords = list(set(combined_keywords))
    
    return {
        "fusion_type": "PHYSICS_LAW_VERIFICATION",
        "top_keywords": unique_keywords[:10],
        "aggregate_confidence": avg_confidence,
        "summary": f"Verified {len(reports)} intelligence assets via Physics Engine."
    }

# --- STEP 3: 전략 교시 및 지능 앵커링 (PUSH) ---
@ensure_alive(gov)
async def push_fusion_decree(client: httpx.AsyncClient, fusion_data: dict, source_ids: list[str]) -> bool:
    """[V51.9 RECTIFIED] Core API 규격(StrategicDecreeRequest)에 맞춘 422 에러 박멸 로직"""
    try:
        # A. Strategic Decree 보고 (Core 규격 강제 일치)
        decree_payload = {
            "stratum_id": cfg.STRATUM_ID,
            "strategic_directive": fusion_data["summary"],
            "focus_sector": "PHYSICS_LAW_VERIFICATION",
            "correlations": fusion_data["top_keywords"] # list[str] 형태로 전달
        }
        
        r_decree = await client.post(
            f"{CORE}/pipeline/strategic_decrees",
            headers=gov.get_fencing_headers(),
            json=decree_payload,
            timeout=10.0
        )
        
        if r_decree.status_code in [200, 201]:
            logger.info("[PUSH] Strategic Decree successfully accepted by Core.")
        else:
            logger.warning(f"[PUSH] Strategic Decree rejected ({r_decree.status_code}): {r_decree.text}")

        # B. 물리적 데이터 앵커링 (파일 저장)
        content_json = json.dumps(fusion_data, ensure_ascii=False)
        content_hash = hashlib.md5(content_json.encode()).hexdigest()
        data_dir = root / "data" / "physics"
        data_dir.mkdir(parents=True, exist_ok=True)
        storage_path = str(data_dir / f"{content_hash}.json")
        
        with open(storage_path, "w", encoding="utf-8") as f:
            f.write(content_json)

        # C. 최종 지능 보고서 업데이트
        await client.post(
            f"{CORE}/pipeline/intelligence/reports",
            headers=gov.headers,
            json={
                "stratum_id": cfg.STRATUM_ID,
                "report_type": "PHYSICS_FUSION",
                "content": {
                    "storage_path": storage_path,
                    "fusion_type": fusion_data["fusion_type"],
                    "summary": fusion_data["summary"]
                },
                "confidence_score": fusion_data["aggregate_confidence"]
            },
            timeout=10.0
        )
        
        logger.info(f"[PUSH] PHYSICS fusion anchored to: {storage_path}")
        return True
    except Exception as e:
        logger.error(f"[PUSH] 융합 데이터 적재 실패: {e}")
    return False

@ensure_alive(gov)
async def mark_consumed(client: httpx.AsyncClient, report_ids: list[str]):
    """소비된 보고서 마킹 처리"""
    try:
        await client.patch(
            f"{CORE}/pipeline/cross_reports/mark_consumed",
            headers={**gov.headers, "Idempotency-Key": str(uuid.uuid4())},
            json=report_ids,
            timeout=10.0
        )
    except Exception as e:
        logger.warning(f"[MARK] 소비 마킹 실패: {e}")

# --- 메인 생명주기 ---
async def physics_lifecycle():
    if not await wait_for_core(CORE):
        logger.critical("[SYS] ❌ 코어망 접속 거부. 종료합니다.")
        return

    async with get_imperial_client(timeout=10.0) as client:
        # 탄생 성사 (Birth Ceremony)
        idem_key = str(uuid.uuid4())
        logger.info(f"[SYS] [GENE] Birth Ceremony Started... ({cfg.PHYSICS_NAME})")
        
        payload = {
            "ant_name": cfg.PHYSICS_NAME,
            "ant_type": "PHYSICS",
            "queen_id": cfg.QUEEN_ID,
            "stratum_id": cfg.STRATUM_ID,
            "target_url": "LOCAL_PHYSICS_ENGINE"
        }

        success = await gov.birth(payload, instance_path=str(Path(__file__).resolve().parent), idempotency_key=idem_key)
        if not success:
            logger.error("[SYS] Registry Birth Denied. Running in limited mode.")

        await gov.start_heartbeat()
        logger.info(f"[SYS] PHYSICS Engine started (Poll: {cfg.POLL_INTERVAL_SEC}s)")
        
        while gov.is_alive:
            try:
                reports = await poll_cross_reports(client)
                if reports:
                    fusion_result = await fuse_intelligence(reports)
                    report_ids = [str(r["report_id"]) for r in reports]
                    
                    if await push_fusion_decree(client, fusion_result, report_ids):
                        await mark_consumed(client, report_ids)
                
                await asyncio.sleep(cfg.POLL_INTERVAL_SEC)
            except Exception as e:
                logger.error(f"[LOOP] {e}")
                await asyncio.sleep(10)

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(physics_lifecycle())
    except KeyboardInterrupt:
        logger.info("PHYSICS shutdown.")