"""
worker_areum.py — AREUM 엣지 AI 분석 워커 (완성 버전)
제국 헌법 API v2.0 / 글로벌 AI 학습 규약 완전 준수

3단계 파이프라인:
  1. POLL — 제국 코어망 API 로 할당된 STRATUM의 미처리 자산(assets)을 수신
  2. ANALYZE — 로컬 Ollama 엔진으로 정수 추출 수행 (지수 백오프 방어)
  3. PUSH — 분석 결과를 STRATUM 테이블 AI 칼럼에 결합(Mutation)하고
             REX용 cross_reports 파이프라인으로 최종 송출
"""

import asyncio
import os
import uuid
import logging
import sys
import json
import sqlite3
import random
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
import httpx



from core.robustness import ImperialGovernance, ensure_alive, get_imperial_client, wait_for_core, retry_ceremony

# ─── 로깅 ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] AREUM %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout
)
logger = logging.getLogger("areum.worker")

# ─── 설정 ───────────────────────────────────────────────────────────────────
class AreumSettings(BaseSettings):
    CORE_HOST: str = "127.0.0.1"
    PORT_CORE_API: str = "8800"
    GATEWAY_TOKEN: str = "mon_gw_ch4ng3m3_bef0re_pr0d"
    STRATUM_ID: str = "UNKNOWN_STRATUM"
    QUEEN_ID: str = "UNKNOWN_QUEEN"
    AREUM_NAME: str = "AREUM-1"
    AREUM_ID: str = Field(default_factory=lambda: f"AREUM-{uuid.uuid4().hex[:8]}")
    OLLAMA_HOST: str = "127.0.0.1"
    OLLAMA_PORT: str = "11434"
    OLLAMA_MODEL: str = "gemma3:4b"
    POLL_INTERVAL_SEC: int = 30   # 30초마다 새 자산 폴링
    BATCH_SIZE: int = 5           # 1회 최대 처리 건수
    model_config = SettingsConfigDict(
        # [V51.5] Priority Chain: 본영(.env) first, then 로컬(.env) for final override
        env_file=[os.path.join(os.path.dirname(__file__), ".env"), ".env"],
        env_file_encoding='utf-8',
        extra="ignore"
    )

cfg = AreumSettings()
CORE = f"http://{cfg.CORE_HOST}:{cfg.PORT_CORE_API}/v1"
OLLAMA = f"http://{cfg.OLLAMA_HOST}:{cfg.OLLAMA_PORT}/api"

AREUM_ID: str = cfg.AREUM_ID

# ─── [V51.5] GOVERNANCE INITIALIZATION ──────────────────────────────────────
gov = ImperialGovernance(
    entity_type="areum", # Use specialized 'areum' type
    entity_id=AREUM_ID,
    core_url=CORE,
    gateway_token=cfg.GATEWAY_TOKEN
)
# Update entity_id after actual birth ceremony

# ─── 결정론적 Ollama 출력 모델 (Pydantic Enforcement) ────────────────────────
class ExtractedEssence(BaseModel):
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="분석 신뢰도")
    keywords: list[str] = Field(..., description="핵심 키워드 목록")
    summary: str = Field(..., description="사실 기반 건조한 요약 (감정 배제)")

# ─── 공통 유틸: 지수 백오프 + Pydantic 검증 ──────────────────────────────────
@ensure_alive(gov)
async def ask_ollama(client: httpx.AsyncClient, text_input: str, max_retries: int = 3) -> ExtractedEssence | None:
    system_prompt = (
        "You are an analytical AI. Extract essence from the provided text. "
        "Respond in valid JSON ONLY matching this exact schema: "
        f"{ExtractedEssence.model_json_schema()}"
        "\nDo NOT use markdown code blocks."
    )
    payload = {
        "model": cfg.OLLAMA_MODEL,
        "prompt": text_input,
        "system": system_prompt,
        "stream": False,
        "format": "json"
    }
    
    # [V51.5] Simulated Cost Injection
    gov.current_session_cost += 0.05 
    
    delay = 2.0
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"[OLLAMA] 분석 시도 {attempt}/{max_retries}...")
            r = await client.post(f"{OLLAMA}/generate", json=payload, timeout=90.0)
            r.raise_for_status()
            essence = ExtractedEssence.model_validate_json(r.json().get("response", ""))
            logger.info(f"[OLLAMA] OK 분석 완료 (신뢰도: {essence.confidence_score:.2f})")
            return essence
        except ValidationError as e:
            logger.warning(f"[OLLAMA] 파싱 에러 (JSON 스키마 불일치 — Attempt {attempt}): {str(e)[:80]}")
        except httpx.TimeoutException:
            logger.warning(f"[OLLAMA] 타임아웃 (Attempt {attempt})")
        except httpx.ConnectError:
            logger.error("[OLLAMA] 연결 실패 — Ollama가 꺼져 있습니까?")
            break
        except Exception as e:
            logger.error(f"[OLLAMA] 알 수 없는 오류: {e}")
        if attempt < max_retries:
            logger.info(f"[OLLAMA] {delay:.0f}초 후 재시도...")
            await asyncio.sleep(delay)
            delay *= 2
    return None

# ─── STEP 1: 코어망에서 미처리 자산 폴링 ─────────────────────────────────────
@ensure_alive(gov)
async def poll_pending_assets(client: httpx.AsyncClient) -> list[dict]:
    """STRATUM 내 ai_summary가 아직 NULL인 자산을 요청"""
    try:
        r = await client.get(
            f"{CORE}/pipeline/assets/pending",
            headers=gov.headers,
            params={"stratum_id": cfg.STRATUM_ID, "limit": cfg.BATCH_SIZE},
            timeout=10.0
        )
        if r.status_code == 200:
            assets = r.json().get("assets", [])
            if assets:
                logger.info(f"[POLL] {len(assets)}건의 미처리 자산 수신.")
            return assets
        elif r.status_code == 404:
            return []
        elif r.status_code == 403:
            logger.error("[POLL] FAIL 403 Forbidden: GATEWAY_TOKEN 이 코어 서버와 일치하지 않습니다.")
            return []
    except Exception as e:
        logger.warning(f"[POLL] 코어망 연결 실패 (서버가 아직 준비되지 않았을 수 있음): {e}")
    return []

# ─── STEP 2+3: 분석 후 칼럼 결합(Mutation) 및 REX 송출(Push) ────────────────
@ensure_alive(gov)
async def process_asset(client: httpx.AsyncClient, asset: dict) -> bool:
    asset_id = asset.get("id")
    storage_path = asset.get("storage_path")
    
    logger.info(f"[PROCESS] 자산 분석 시작: {asset_id} (Path: {storage_path or 'CLOUD-ONLY'})")
    
    # [V51.5] Hybrid Data Loading
    raw_text = ""
    if storage_path and Path(storage_path).exists():
        try:
            with open(storage_path, "r", encoding="utf-8") as f:
                local_data = json.load(f)
                # 우선순위: essence > raw_html > text
                raw_text = local_data.get("essence") or local_data.get("raw_html") or local_data.get("text", "")
            logger.info(f"[HYBRID] Local storage hit: {len(raw_text)} chars loaded.")
        except Exception as e:
            logger.error(f"[HYBRID] Local file read failed: {e}")
            raw_text = json.dumps(asset.get("raw_data", {}), ensure_ascii=False)
    else:
        raw_text = json.dumps(asset.get("raw_data", {}), ensure_ascii=False)
    
    if not raw_text or raw_text == "null":
        logger.warning(f"[PROCESS] No data found for asset {asset_id}. Skipping.")
        return False

    # STEP 2: 로컬 Ollama 분석
    essence = await ask_ollama(client, raw_text[:30000]) # Token limit safety
    if not essence:
        logger.error(f"[PROCESS] FAIL 자산 {asset_id} 분석 실패. 건너뜀.")
        return False

    # STEP 3a: STRATUM 테이블 AI 칼럼 결합 (Mutation)
    try:
        r = await client.patch(
            f"{CORE}/pipeline/assets/{asset_id}/areum",
            headers=gov.get_fencing_headers(),
            json={
                "stratum_id": cfg.STRATUM_ID,
                "areum_id": gov.entity_id,
                "ai_summary": essence.summary,
                "essence_tags": essence.keywords,
                "ai_confidence": essence.confidence_score,
            },
            timeout=10.0
        )
        if r.status_code not in (200, 204):
            logger.warning(f"[MUTATE] 칼럼 결합 응답 이상: {r.status_code}")
    except Exception as e:
        logger.warning(f"[MUTATE] 칼럼 결합 실패: {e}")

    # STEP 3b: REX 파이프라인 테이블로 보고서 송출 (Push)
    try:
        r = await client.post(
            f"{CORE}/pipeline/cross_reports",
            headers={**gov.get_fencing_headers(), "Idempotency-Key": str(uuid.uuid4())},
            json={
                "areum_id": gov.entity_id,
                "stratum_id": cfg.STRATUM_ID,
                "source_asset_id": asset_id,
                "ollama_model": cfg.OLLAMA_MODEL,
                "confidence_score": essence.confidence_score,
                "keywords": essence.keywords,
                "summary": essence.summary,
                "raw_essence": {"model_output": essence.model_dump()}
            },
            timeout=10.0
        )
        r.raise_for_status()
        logger.info(f"[PUSH] OK Core Pipeline 보고서 적재 완료: {r.json().get('report_id', '?')}")
        
    except Exception as e:
        logger.error(f"[PUSH/REX] REX 송출 실패: {e}")
        return False

    # 무상태 증발 (Stateless Evaporation)
    del raw_text
    del essence
    return True

# ─── 생명주기 메인 루프 ───────────────────────────────────────────────────────
async def worker_lifecycle():
    # [FORTIFICATION] Wait for Core API reachability 
    if not await wait_for_core(CORE):
        logger.critical("[SYS] FAIL 코어망 응답 없거나 접속 거부됨. 강제 종료합니다.")
        return

    # [FORTIFICATION] Using Imperial Standardized Client
    async with get_imperial_client(timeout=10.0) as client:
        # [V51.5] Unified Birth Ceremony
        idem_key = str(uuid.uuid4())
        logger.info(f"[SYS] [GENE] Birth Ceremony Started... ({cfg.AREUM_NAME})")
        
        payload = {
            "areum_name": cfg.AREUM_NAME,
            "stratum_id": cfg.STRATUM_ID,
            "queen_id": cfg.QUEEN_ID,
            "ollama_model": cfg.OLLAMA_MODEL,
            "target_url": f"LOCAL_OLLAMA/{cfg.OLLAMA_MODEL}"
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
        logger.info(f"[SYS] [V51.5] Governance Active. Heartbeat started.")

        logger.info(f"[SYS] [LOOP] Polling Started (Interval: {cfg.POLL_INTERVAL_SEC}s)")
        processed_count = 0
        try:
            while gov.is_alive:
                try:
                    # [V51.5] Infrastructure Mercy: Governor Loop Timeout (10s)
                    async with asyncio.timeout(10.0):
                        assets = await poll_pending_assets(client)
                        for asset in assets:
                            if not gov.is_alive: break
                            ok = await process_asset(client, asset)
                            if ok:
                                processed_count += 1
                except asyncio.TimeoutError:
                    logger.warning("[SYS] Governor loop timeout (10s). Backing off.")
                except Exception as e:
                    logger.error(f"[SYS] Loop error: {e}")

                await asyncio.sleep(cfg.POLL_INTERVAL_SEC)

        except asyncio.CancelledError:
            logger.info("[SYS] 종료 명령 수신.")
        finally:
            if gov.is_alive:
                try:
                    await client.delete(f"{CORE}/registry/death/ant/{gov.entity_id}",
                        headers=gov.headers, json={"reason": "TASK_COMPLETE"}, timeout=5.0)
                    logger.info(f"[SYS] 💀 사망 신고 완료. (총 {processed_count}건 처리)")
                except Exception:
                    pass

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(worker_lifecycle())
    except KeyboardInterrupt:
        logger.info("Ctrl+C 감지. 수동 종료.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(worker_lifecycle())
    except KeyboardInterrupt:
        logger.info("Ctrl+C 감지. 수동 종료.")
