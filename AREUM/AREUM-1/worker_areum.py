# 🏛️ [IMPERIAL DIRECTIVE: AREUM-PRIME V1.0 - SYNCED & PRESERVED]
# c:\monewment\AREUM\AREUM-1\worker_areum.py
# "Zero-Entropy Intelligence Synthesis & Hallucination Shield"

import asyncio
import os
import uuid
import logging
import sys
import json
import re
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
import httpx

from core.robustness import ImperialGovernance, ensure_alive, get_imperial_client, wait_for_core

# ─── 로깅 시스템 ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] 🧪 PRIME-AREUM %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout
)
logger = logging.getLogger("areum.prime")

# ─── MODULE 1: ROBUST SKELETON (설정 및 거버넌스) ─────────────────────────────
class AreumPrimeSettings(BaseSettings):
    CORE_HOST: str = "127.0.0.1"
    PORT_CORE_API: str = "8800"
    GATEWAY_TOKEN: str = "mon_gw_ch4ng3m3_bef0re_pr0d"
    STRATUM_ID: str = "UNKNOWN_STRATUM"
    STRATUM_DOMAIN: str = "General"  # Options: Novel, Recipe, Commerce, General
    QUEEN_ID: str = "UNKNOWN_QUEEN"
    AREUM_NAME: str = "AREUM-PRIME-1"
    AREUM_ID: str = Field(default_factory=lambda: f"AREUM-{uuid.uuid4().hex[:8]}")
    OLLAMA_HOST: str = "127.0.0.1"
    OLLAMA_PORT: str = "11434"
    OLLAMA_MODEL: str = "gemma3:4b"
    POLL_INTERVAL_SEC: int = 15
    BATCH_SIZE: int = 5
    
    model_config = SettingsConfigDict(
        env_file=[os.path.join(os.path.dirname(__file__), ".env"), ".env"],
        env_file_encoding='utf-8',
        extra="ignore"
    )

cfg = AreumPrimeSettings()
CORE = f"http://{cfg.CORE_HOST}:{cfg.PORT_CORE_API}/v1"
OLLAMA = f"http://{cfg.OLLAMA_HOST}:{cfg.OLLAMA_PORT}/api"

# ─── 거버넌스 엔진 초기화 ────────────────────────────────────────────────────
gov = ImperialGovernance(
    entity_type="areum",
    entity_id=cfg.AREUM_ID,
    core_url=CORE,
    gateway_token=cfg.GATEWAY_TOKEN
)

# ─── SCHEMA: ENTROPY SHIELD (데이터 모델) ──────────────────────────────────
class ExtractedEssence(BaseModel):
    """지능 정수 모델 (V51.6: Pydantic 가드레일 강화)"""
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    keywords: list[str] = Field(default_factory=list)
    summary: str = Field(default="No summary generated")
    key_facts: list[str] = Field(default_factory=list)
    risk_level: str = Field(default="LOW")  # LOW, MEDIUM, HIGH, CRITICAL

# ─── MODULE 2: ADAPTIVE INTELLIGENCE (도메인 특화 두뇌) ──────────────────────
def get_adaptive_prompt(domain: str) -> str:
    prompts = {
        "Novel": (
            "You are a literary alchemist. Analyze the text for subtext, motifs, "
            "and character motivations. Focus on 'thematic weight'."
        ),
        "Recipe": (
            "You are a molecular gastronomist. Analyze the text for ingredient synergy, "
            "chemical balance, and procedure precision. Focus on 'aromatic logic'."
        ),
        "Commerce": (
            "You are a strategic economist. Analyze the text for market edge, "
            "scarcity flags, and customer psychology. Focus on 'competitive dominance'."
        ),
        "General": (
            "You are an empirical investigator. Analyze the text for logical consistency, "
            "verifiable facts, and potential risks. Focus on 'objective truth'."
        )
    }
    base = prompts.get(domain, prompts["General"])
    return (
        f"{base}\n"
        "You MUST return a JSON object with 'confidence_score', 'keywords', 'summary', 'key_facts', and 'risk_level' keys.\n"
        f"Schema: {ExtractedEssence.model_json_schema()}\n"
        "Provide ONLY the raw JSON object. No conversational fillers."
    )

# ─── MODULE 3: ENTROPY SHIELD (추출 및 환각 탐지) ───────────────────────────
def detect_hallucinations(essence: ExtractedEssence, raw_text: str) -> ExtractedEssence:
    """AI가 지어낸 거짓 정보(환각)를 실제 텍스트와 대조하여 탐지"""
    if not essence.key_facts or not raw_text:
        return essence

    valid_facts = 0
    raw_lower = raw_text.lower()
    
    for fact in essence.key_facts:
        words = [w for w in re.findall(r'\w+', fact.lower()) if len(w) > 1]
        if not words: continue
        
        matches = sum(1 for w in words if w in raw_lower)
        if matches / len(words) > 0.6: 
            valid_facts += 1

    valid_ratio = valid_facts / len(essence.key_facts) if essence.key_facts else 1.0
    
    if valid_ratio < 0.5:
        logger.warning(f"[SHIELD] Hallucination detected! (Purity: {valid_ratio:.2f}). Penalizing.")
        essence.risk_level = "CRITICAL"
        essence.confidence_score = 0.1
    elif valid_ratio < 0.8:
        essence.risk_level = "MEDIUM"
        essence.confidence_score *= 0.7
        
    return essence

@ensure_alive(gov)
async def ask_ollama(client: httpx.AsyncClient, text_input: str) -> ExtractedEssence | None:
    system_prompt = get_adaptive_prompt(cfg.STRATUM_DOMAIN)
    payload = {
        "model": cfg.OLLAMA_MODEL,
        "prompt": text_input,
        "system": system_prompt,
        "stream": False,
        "format": "json"
    }
    
    gov.current_session_cost += 0.05 
    
    for attempt in range(1, 4):
        try:
            r = await client.post(f"{OLLAMA}/generate", json=payload, timeout=90.0)
            r.raise_for_status()
            
            raw_response = r.json().get("response", "")
            
            # [CRITICAL] Surgical JSON Extractor
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                clean_json = json_match.group(0)
            else:
                clean_json = raw_response

            essence = ExtractedEssence.model_validate_json(clean_json)
            essence = detect_hallucinations(essence, text_input)
            
            return essence
            
        except Exception as e:
            logger.warning(f"[OLLAMA] Attempt {attempt} failed: {e}")
            await asyncio.sleep(2)
            
    return None

# ─── MODULE 4: ATOMIC PUSH (이중 적재 프로토콜 - SURGICALLY SYNCED) ───────
@ensure_alive(gov)
async def process_asset(client: httpx.AsyncClient, asset: dict) -> bool:
    asset_id = asset.get("id")
    storage_path = asset.get("storage_path")
    
    # 데이터 로딩
    raw_text = ""
    if storage_path and Path(storage_path).exists():
        try:
            with open(storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                raw_text = data.get("essence") or data.get("raw_html") or data.get("text", "")
        except: pass
    
    if not raw_text:
        raw_text = json.dumps(asset.get("raw_data", {}), ensure_ascii=False)
        
    if not raw_text or raw_text == "null": return False

    # 분석 시퀀스
    essence = await ask_ollama(client, raw_text[:30000])
    if not essence: return False

    # A. STRATUM Mutation (Patch)
    try:
        await client.patch(
            f"{CORE}/pipeline/assets/{asset_id}/areum",
            headers=gov.get_fencing_headers(),
            json={
                "stratum_id": cfg.STRATUM_ID,
                "areum_id": gov.entity_id,
                "ai_summary": essence.summary,
                "essence_tags": essence.keywords,
                "ai_confidence": essence.confidence_score,
            },
            timeout=5.0
        )
    except: pass

    # B. Intelligence Report Push (Post) - [V51.6 RECTIFIED SYNC]
    # TARGET: {CORE}/pipeline/intelligence/reports
    try:
        r = await client.post(
            f"{CORE}/pipeline/intelligence/reports",
            headers=gov.get_fencing_headers(),
            json={
                "stratum_id": cfg.STRATUM_ID,
                "report_type": "AREUM_ANALYSIS",
                "content": {
                    "summary": essence.summary,
                    "keywords": essence.keywords,
                    "key_facts": essence.key_facts,
                    "risk_level": essence.risk_level,
                    "ollama_model": cfg.OLLAMA_MODEL,
                    "source_asset_id": asset_id
                },
                "confidence_score": essence.confidence_score
            },
            timeout=10.0
        )
        r.raise_for_status()
        logger.info(f"[PUSH] Intelligence Report Loaded (Score: {essence.confidence_score:.2f})")
        return True
    except Exception as e:
        logger.error(f"[PUSH] API Sync Failed (404/500): {e}")
        return False

# ─── MAIN LIFECYCLE ──────────────────────────────────────────────────────────
async def worker_lifecycle():
    await wait_for_core(CORE)
    
    async with get_imperial_client(timeout=10.0) as client:
        # [CRITICAL BIRTH] areum_id와 stratum_id 명시적 주입
        payload = {
            "areum_id": cfg.AREUM_ID,
            "stratum_id": cfg.STRATUM_ID,
            "areum_name": cfg.AREUM_NAME,
            "queen_id": cfg.QUEEN_ID,
            "ollama_model": cfg.OLLAMA_MODEL,
            "domain": cfg.STRATUM_DOMAIN
        }

        success = await gov.birth(payload, instance_path=str(Path(__file__).resolve().parent))
        if not success: 
            logger.critical("Birth rejected by Core API.")
            return

        await gov.start_heartbeat()
        logger.info(f"[SYS] AREUM-PRIME ({gov.entity_id}) is now ACTIVE in {cfg.STRATUM_DOMAIN} domain.")

        while gov.is_alive:
            try:
                # Poll pending assets
                r = await client.get(
                    f"{CORE}/pipeline/assets/pending",
                    headers=gov.headers,
                    params={"stratum_id": cfg.STRATUM_ID, "limit": cfg.BATCH_SIZE}
                )
                if r.status_code == 200:
                    assets = r.json().get("assets", [])
                    for asset in assets:
                        if not gov.is_alive: break
                        await process_asset(client, asset)
            except Exception as e:
                logger.error(f"[LOOP] {e}")
            
            await asyncio.sleep(cfg.POLL_INTERVAL_SEC)

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(worker_lifecycle())
    except KeyboardInterrupt:
        logger.info("Termination sequence initiated.")