import asyncio
import json
import logging
import os
import sys
import uuid
import httpx
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# --- [PATH RESOLUTION] ---
root = Path(__file__).resolve().parent.parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from core.robustness import get_imperial_client, wait_for_core
from pydantic_settings import BaseSettings, SettingsConfigDict
from core.intelligence_schemas import Essence

# --- [CONFIGURATION: V2 STANDARDS] ---
class AreumV2Settings(BaseSettings):
    STRATUM_DOMAIN: str = "General"
    ANALYSIS_GUIDE: str = "Extract key facts objectively. Adapting to the data structure."
    CORE_API_URL: str = "http://127.0.0.1:8800/v1"
    OLLAMA_API_URL: str = "http://127.0.0.1:11434/api"
    GATEWAY_TOKEN: str = "mon_gw_ch4ng3m3_bef0re_pr0d"
    STRATUM_ID: str = "UNKNOWN"
    AREUM_MODEL: str = "monewment-areum"
    POLL_INTERVAL: int = 15
    BATCH_SIZE: int = 10
    CONFIDENCE_THRESHOLD: float = 0.6
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

cfg = AreumV2Settings()
logging.basicConfig(level=logging.INFO, format="[AREUM-V2] %(levelname)s: %(message)s")
logger = logging.getLogger("areum_v2")

# --- [RESOURCE DISCIPLINE] ---
_CLIENT: Optional[httpx.AsyncClient] = None

def get_session() -> httpx.AsyncClient:
    global _CLIENT
    if _CLIENT is None or _CLIENT.is_closed:
        _CLIENT = httpx.AsyncClient(timeout=120.0, limits=httpx.Limits(max_connections=50))
    return _CLIENT

# --- [ADAPTIVE SENSORY CORE] ---
async def digest_fluid_payload(raw_payload: Dict[str, Any]) -> Optional[Essence]:
    """
    Polymorphic digestion of schemaless data.
    Self-parses the raw_payload based on ANALYSIS_GUIDE.
    """
    client = get_session()
    
    # 🏛️ Fluid Intelligence Protocol
    # We pass the entire JSON-ified payload and let the sensory unit decide the importance.
    payload_str = json.dumps(raw_payload, ensure_ascii=False, indent=2)
    
    system_prompt = (
        f"너는 {cfg.STRATUM_DOMAIN} 전문 지능 AREUM-V2이다.\n"
        f"분석 칙령 (ANALYSIS_GUIDE): {cfg.ANALYSIS_GUIDE}\n"
        "데이터는 비정형(Schemaless)이다. 스스로 구조를 파악하고 핵심 정보를 추출하라.\n"
        "결과물은 반드시 다음 JSON 규격을 준수해야 한다.\n"
        "{\n"
        "  \"target_subject\": \"분석된 핵심 개체/주제\",\n"
        "  \"sentiment_score\": -1.0 ~ 1.0,\n"
        "  \"key_facts\": [\"데이터에서 발견한 핵심 사실들\"],\n"
        "  \"risk_level\": \"LOW/MEDIUM/HIGH/CRITICAL\",\n"
        "  \"confidence\": 0.0 ~ 1.0\n"
        "}"
    )
    
    ollama_request = {
        "model": cfg.AREUM_MODEL,
        "prompt": f"Fluid Asset Payload to Digest:\n{payload_str}",
        "system": system_prompt,
        "stream": False,
        "format": "json"
    }
    
    delay = 1.0
    for attempt in range(1, 4):
        try:
            r = await client.post(f"{cfg.OLLAMA_API_URL}/generate", json=ollama_request)
            r.raise_for_status()
            
            # Deterministic Validation
            essence = Essence.model_validate_json(r.json().get("response", ""))
            
            # 2차 검증: Entropy Shield (Hallucination filtering)
            if essence.confidence < cfg.CONFIDENCE_THRESHOLD:
                logger.warning(f"Symmetry breach: Confidence {essence.confidence} below threshold.")
                return None
            
            # 3차 검증: Forgery Detection (Reverse-matching)
            # AREUM이 보고한 key_facts가 실제 원본 데이터에 근거하는지 검사
            raw_text_lower = str(raw_payload).lower()
            hallucination_count = 0
            for fact in essence.key_facts:
                if fact.lower() not in raw_text_lower and not any(kw.lower() in raw_text_lower for kw in fact.split()):
                    hallucination_count = hallucination_count + 1
            
            if hallucination_count > len(essence.key_facts) / 2:
                logger.error(f"🔴 [CRITICAL] Hallucination Detected! Facts: {essence.key_facts}")
                essence.risk_level = "CRITICAL"
                essence.confidence = 0.1
                # 제국 법도에 따라 폐기하거나 경고 마킹
            
            # Traceability Injection
            essence.metadata = {
                "source_domain": cfg.STRATUM_DOMAIN,
                "ingested_v2": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            return essence
            
        except Exception as e:
            logger.warning(f"[IMPERIAL-RETRY] Attempt {attempt} failed: {e}")
            await asyncio.sleep(delay)
            delay *= 2.0
            
    logger.error("Pathological failure: Sensory unit exhausted.")
    return None

async def lifecycle_loop():
    logger.info(f"AREUM-V2 (Fluid Sensory) Activated. Domain: {cfg.STRATUM_DOMAIN}")
    
    # [FORTIFICATION] Using Imperial Standardized Client and Wait Loop
    if not await wait_for_core(cfg.CORE_API_URL):
        logger.critical("❌ Core Hub isolation detected. Shutting down cells.")
        return

    headers = {"X-Queen-Token": cfg.GATEWAY_TOKEN}
    
    async with get_imperial_client(timeout=120.0) as client:
        while True:
            try:
                # 1. Poll UNPROCESSED fluid assets
                r = await client.get(
                    f"{cfg.CORE_API_URL}/pipeline/assets/fluid/pending", 
                    headers=headers, 
                    params={"stratum_id": cfg.STRATUM_ID, "limit": cfg.BATCH_SIZE}
                )
                assets = r.json().get("assets", [])
                
                if not assets:
                    await asyncio.sleep(cfg.POLL_INTERVAL)
                    continue
                
                for asset in assets:
                    asset_id = asset["id"]
                    raw_payload = asset["raw_payload"]
                    
                    # 2. Digest (Polymorphic Intelligence)
                    essence = await digest_fluid_payload(raw_payload)
                    
                    # Explicit Memory Clear
                    del raw_payload
                    
                    if not essence: continue
                    
                    # 3. Double-Push Protocol
                    # A. Update Asset (Local Summary)
                    await client.patch(
                        f"{cfg.CORE_API_URL}/pipeline/assets/fluid/{asset_id}", 
                        headers=headers,
                        json={
                            "ai_summary": f"[{essence.risk_level}] {essence.target_subject}",
                            "is_processed": True
                        }
                    )
                    
                    # B. Transmit to Cross-Domain Pipeline
                    await client.post(
                        f"{cfg.CORE_API_URL}/pipeline/cross_reports", 
                        headers={**headers, "Idempotency-Key": str(uuid.uuid4())},
                        json={
                            "areum_id": f"AREUM-V2-{cfg.STRATUM_DOMAIN.upper()}",
                            "stratum_id": cfg.STRATUM_ID,
                            "source_asset_id": asset_id,
                            "confidence_score": essence.confidence,
                            "keywords": essence.key_facts,
                            "summary": essence.model_dump_json() # Exact relay to REX
                        }
                    )
                    
                    logger.info(f"[IMPERIAL-LOG] Fluid Asset {asset_id[:8]} Digested. Subject: {essence.target_subject}")

            except Exception as e:
                logger.error(f"Integrity Breach: {e}")
                await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(lifecycle_loop())
    except KeyboardInterrupt:
        logger.info("AREUM-V2 returning to core dormancy.")
