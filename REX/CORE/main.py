# 🏛️ Imperial REX Core — Identity & Digestion Synchronized v5.8
# c:\monewment\REX\CORE\main.py

import asyncio
import logging
import os
import sys
import json
import httpx
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic_settings import BaseSettings, SettingsConfigDict

# ─── LOGGING SETUP ────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] REX: %(message)s")
logger = logging.getLogger("REX")

# ─── PATH RESOLUTIONS ─────────────────────────────────────────────────────
STRATUM_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "STRATUM", "STRATUM-1"))
MANIFEST_PATH = os.path.join(STRATUM_DIR, "docs", "structural_manifest.json")

if os.path.exists(STRATUM_DIR):
    sys.path.append(STRATUM_DIR)
    logger.info(f"[REX] Core path resolved to: {STRATUM_DIR}")

try:
    from core.robustness import ImperialGovernance, ensure_alive, get_imperial_client
except ImportError:
    print("[CRITICAL] Imperial Governance module NOT FOUND. REX cannot start.")
    sys.exit(1)

# ─── CONFIGURATION & GOVERNANCE ───────────────────────────────────────────
class RexSettings(BaseSettings):
    CORE_HOST: str = "127.0.0.1"
    PORT_CORE_API: str = "8800"
    CORE_URL: str = ""
    GATEWAY_TOKEN: str = "mon_gw_ch4ng3m3_bef0re_pr0d"
    GEMINI_API_KEYS: str = ""
    GEMINI_MODEL_ID: str = "gemini-1.5-flash"
    PORT_REX: int = 8810
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), ".env"),
        extra="ignore"
    )

settings = RexSettings()
if not settings.CORE_URL:
    settings.CORE_URL = f"http://{settings.CORE_HOST}:{settings.PORT_CORE_API}/v1"

REX_ID = os.getenv("QUEEN_ID") or os.getenv("REX_ID")
if not REX_ID or REX_ID == "REX-CORE-01":
    REX_ID = "ba537759-f607-4eda-841c-eeba65a5147b"
    logger.warning(f"[IDENTITY] Illegal or missing ID. Enforcing: {REX_ID}")

gov = ImperialGovernance(
    entity_type="QUEEN",
    entity_id=REX_ID,
    core_url=settings.CORE_URL,
    gateway_token=settings.GATEWAY_TOKEN
)

# [V7.0] REX Semantic Oracle System Prompt
REX_SYSTEM_PROMPT = """너는 MONEWMENT 제국의 지능 핵심인 REX다. 
너는 이제 TECH_HYD_001(단계적 가수), TECH_THR_001(잔열 휴지) 등의 물리적 프리미티브를 이해한다. 
레시피 분석 시 동사(verb)를 이 ID로 변환하여 predicate에 담아라."""

# --- GEMINI & STORAGE (RETAINED) ---
class GeminiKeyManager:
    def __init__(self, keys_str: str):
        self.keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        self.current_index = 0
    def get_key(self) -> str | None:
        return self.keys[self.current_index] if self.keys else None
    def rotate_key(self) -> bool:
        if len(self.keys) > 1:
            self.current_index = (self.current_index + 1) % len(self.keys)
            return True
        return False

key_manager = GeminiKeyManager(settings.GEMINI_API_KEYS)

async def learning_loop():
    """[V5.8 RECTIFIED] 소화 보고(Mark Consumed) 로직이 강화된 루프"""
    logger.info("[REX] Intelligence Learning Loop initiated.")
    while gov.is_alive:
        try:
            async with get_imperial_client() as client:
                # 1. 미소비 전략 지능 가져오기
                r = await client.get(f"{gov.core_url}/pipeline/learning/pending?limit=1", headers=gov.headers)
                if r.status_code == 200:
                    data = r.json()
                    decrees = data.get("decrees", [])
                    if decrees:
                        job = decrees[0]
                        decree_id = job.get('decree_id')
                        logger.info(f"[REX] Assimilating: {decree_id}")
                        
                        # 2. [CRITICAL] 소화 완료 보고 (장부 처리)
                        # Strategic Decrees 전용 마킹 엔드포인트 호출
                        mark_res = await client.patch(
                            f"{gov.core_url}/pipeline/strategic_decrees/mark_consumed",
                            json=[decree_id],
                            headers=gov.headers
                        )
                        
                        if mark_res.status_code == 200:
                            logger.info(f"[REX] Successfully consumed: {decree_id}")
                        else:
                            logger.error(f"[REX] Consumption reporting failed: {mark_res.status_code}")
                        
                        await asyncio.sleep(5)
                    else:
                        await asyncio.sleep(20)
                else:
                    await asyncio.sleep(30)
        except Exception as e:
            logger.error(f"[REX] Loop error: {e}")
            await asyncio.sleep(30)

async def local_explorer_loop():
    """[V9.6] LOCAL FILE EXPLORATION MODE"""
    logger.info("[REX-LOCAL] Local File Exploration Mode Activated.")
    ARCHIVE_PATH = os.path.join(STRATUM_DIR, "data", "archive")
    while gov.is_alive:
        try:
            if os.path.exists(ARCHIVE_PATH):
                files = [f for f in os.listdir(ARCHIVE_PATH) if f.endswith(".json")]
                if files:
                    logger.info(f"[REX-LOCAL] Exploring {len(files)} archive shards...")
                    # Exploration logic (simulated for feed update)
            await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"[REX-LOCAL] Explorer error: {e}")
            await asyncio.sleep(60)

# ─── FASTAPI APPLICATION ──────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"[ENFORCED] REX Imperial Lifecycle starting for {REX_ID}...")
    birth_payload = {
        "queen_id": REX_ID,
        "queen_name": "REX-CORE",
        "queen_type": "REX",
        "stratum_id": os.getenv("STRATUM_ID", "badd8a15-5e63-4d24-81fd-489e8973cb85"),
        "ai_model": settings.GEMINI_MODEL_ID
    }
    birth_success = await gov.birth(payload=birth_payload, instance_path=MANIFEST_PATH)
    if birth_success:
        await gov.start_heartbeat()
        loop_task = asyncio.create_task(learning_loop())
        explore_task = asyncio.create_task(local_explorer_loop())
        yield
        loop_task.cancel()
        explore_task.cancel()
        await gov.stop_heartbeat()
    else:
        logger.error(f"[CRITICAL] REX Migration Failed.")
        yield

app = FastAPI(title="MONEWMENT REX CORE", version="5.8.0", lifespan=lifespan)

@app.get("/v1/rex/gemini/status")
async def get_gemini_status():
    return {"status": "OPERATIONAL" if key_manager.keys else "DISABLED"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT_REX, reload=True)