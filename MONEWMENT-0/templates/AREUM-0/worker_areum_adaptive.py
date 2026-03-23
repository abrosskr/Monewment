import asyncio
import json
import logging
import os
import sys
import uuid
import httpx
from pathlib import Path
from typing import Optional

# --- [PATH RESOLUTION] ---
root = Path(__file__).resolve().parent.parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from pydantic_settings import BaseSettings, SettingsConfigDict
from core.intelligence_schemas import Essence

# --- [CONFIGURATION] ---
class AreumSettings(BaseSettings):
    STRATUM_DOMAIN: str = "General"
    ANALYSIS_GUIDE: str = "Extract key facts objectively."
    CORE_API_URL: str = "http://127.0.0.1:8800/v1"
    OLLAMA_API_URL: str = "http://127.0.0.1:11434/api"
    GATEWAY_TOKEN: str = "mon_gw_ch4ng3m3_bef0re_pr0d"
    STRATUM_ID: str = "UNKNOWN"
    AREUM_MODEL: str = "monewment-areum"
    POLL_INTERVAL: int = 15
    BATCH_SIZE: int = 5
    CONFIDENCE_THRESHOLD: float = 0.6
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

cfg = AreumSettings()
logging.basicConfig(level=logging.INFO, format="[AREUM-ADAPTIVE] %(levelname)s: %(message)s")
logger = logging.getLogger("areum_adaptive")

# --- [RESOURCE DISCIPLINE: PERSISTENT SESSION] ---
_CLIENT: Optional[httpx.AsyncClient] = None

def get_session() -> httpx.AsyncClient:
    global _CLIENT
    if _CLIENT is None or _CLIENT.is_closed:
        _CLIENT = httpx.AsyncClient(timeout=120.0, limits=httpx.Limits(max_connections=50))
    return _CLIENT

# --- [ADAPTIVE CORE: ZERO-ENTROPY PROTOCOL] ---
async def extract_essence_deterministic(raw_text: str) -> Optional[Essence]:
    """
    Polymorphic intelligence with Fail-Safe Isolation.
    Ensures deterministic output via format='json'.
    """
    client = get_session()
    
    # Dynamic Persona Composition
    domain_insights = {
        "Novel": "집중 분석 항목: 복선(Forshadowing), 인물 동기, 플롯의 대칭성.",
        "Recipe": "집중 분석 항목: 식재료 농도, 조리 온도, 영양적 조화.",
        "Commerce": "집중 분석 항목: 가격 저항선, 소비자 심리, 경쟁 우위.",
        "General": "집중 분석 항목: 객관적 사실, 논리적 모순, 위험 요소."
    }
    
    guidance = domain_insights.get(cfg.STRATUM_DOMAIN, domain_insights["General"])
    
    system_prompt = (
        f"너는 {cfg.STRATUM_DOMAIN} 전문 지능 AREUM-V2이다.\n"
        f"분석 전략: {guidance}\n"
        f"특수 지침: {cfg.ANALYSIS_GUIDE}\n"
        "결과물은 반드시 다음 JSON 규격을 준수해야 한다.\n"
        "{\n"
        "  \"target_subject\": \"핵심 주제\",\n"
        "  \"sentiment_score\": -1.0 ~ 1.0,\n"
        "  \"key_facts\": [\"사실1\", \"사실2\"],\n"
        "  \"risk_level\": \"LOW/MEDIUM/HIGH/CRITICAL\",\n"
        "  \"confidence\": 0.0 ~ 1.0\n"
        "}"
    )
    
    payload = {
        "model": cfg.AREUM_MODEL,
        "prompt": f"Data to analyze:\n{raw_text}",
        "system": system_prompt,
        "stream": False,
        "format": "json"
    }
    
    # Exponential Backoff for Isolation
    delay = 1.0
    for attempt in range(1, 4):
        try:
            r = await client.post(f"{cfg.OLLAMA_API_URL}/generate", json=payload)
            r.raise_for_status()
            
            # 1차 검증: Pydantic Validation
            essence = Essence.model_validate_json(r.json().get("response", ""))
            
            # 2차 검증: Entropy Shield (Hallucination filtering)
            if essence.confidence < cfg.CONFIDENCE_THRESHOLD:
                logger.warning(f"Report rejected due to low confidence: {essence.confidence}")
                return None
            
            # Traceability Injection
            essence.metadata = {
                "stratum_domain": cfg.STRATUM_DOMAIN,
                "model": cfg.AREUM_MODEL,
                "timestamp": datetime.now().isoformat() if 'datetime' in globals() else str(time.time()),
                "raw_hash": hash(raw_text)
            }
            return essence
            
        except Exception as e:
            logger.warning(f"Ollama attempt {attempt} failed: {e}. Isolation active in {delay}s.")
            await asyncio.sleep(delay)
            delay *= 2.0
            
    logger.error("Imperial Extraction Failed. Entropy limit exceeded.")
    return None

async def lifecycle_loop():
    logger.info(f"AREUM-ADAPTIVE Activated | Domain: {cfg.STRATUM_DOMAIN}")
    headers = {"X-Queen-Token": cfg.GATEWAY_TOKEN}
    
    while True:
        try:
            client = get_session()
            # 1. Atomic Polling
            r = await client.get(
                f"{cfg.CORE_API_URL}/pipeline/assets/pending", 
                headers=headers, 
                params={"stratum_id": cfg.STRATUM_ID, "limit": cfg.BATCH_SIZE}
            )
            assets = r.json().get("assets", [])
            
            if not assets:
                await asyncio.sleep(cfg.POLL_INTERVAL)
                continue
            
            for asset in assets:
                asset_id = asset["id"]
                raw_data_str = json.dumps(asset["raw_data"], ensure_ascii=False)
                
                # 2. Intelligence Synthesis
                essence = await extract_essence_deterministic(raw_data_str)
                
                # Explicit Memory Management
                del raw_data_str 
                
                if not essence: continue
                
                # 3. Double-Push Protocol (Local & Central)
                # Mutation
                await client.patch(
                    f"{cfg.CORE_API_URL}/pipeline/assets/{asset_id}/areum", 
                    headers=headers,
                    json={
                        "areum_id": f"AREUM-{cfg.STRATUM_DOMAIN.upper()}-{cfg.STRATUM_ID[:4]}",
                        "ai_summary": f"[{essence.risk_level}] {essence.target_subject}",
                        "essence_tags": essence.key_facts,
                        "ai_confidence": essence.confidence
                    }
                )
                
                # Cross-Domain Push
                await client.post(
                    f"{cfg.CORE_API_URL}/pipeline/cross_reports", 
                    headers={**headers, "Idempotency-Key": str(uuid.uuid4())},
                    json={
                        "areum_id": f"AREUM-{cfg.STRATUM_DOMAIN.upper()}",
                        "stratum_id": cfg.STRATUM_ID,
                        "source_asset_id": asset_id,
                        "confidence_score": essence.confidence,
                        "keywords": essence.key_facts,
                        "summary": essence.model_dump_json() # Zero-Loss relay
                    }
                )
                
                logger.info(f"✅ Success: {asset_id[:8]} | Sentiment: {essence.sentiment_score} | Confidence: {essence.confidence}")

        except Exception as e:
            logger.error(f"Global Integrity Breach: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    import time
    from datetime import datetime
    try:
        asyncio.run(lifecycle_loop())
    except KeyboardInterrupt:
        logger.info("AREUM withdrawal acknowledged.")
