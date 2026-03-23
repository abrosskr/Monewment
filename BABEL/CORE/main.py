import asyncio, logging, os, sys, httpx, json, re
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict

# [INFRA] MONEWMENT CORE REFERENCE
STRATUM_PATH = r"C:\monewment\STRATUM\STRATUM-1"
if STRATUM_PATH not in sys.path:
    sys.path.append(STRATUM_PATH)

from core.robustness import ImperialGovernance, ensure_alive, get_imperial_client
from knowledge_manager import SovereignKnowledge

class BabelSettings(BaseSettings):
    QUEEN_ID: str; QUEEN_NAME: str; STRATUM_ID: str; CORE_URL: str
    GATEWAY_TOKEN: str; PORT_BABEL: int; BUDGET_LIMIT: float
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

conf = BabelSettings()
logger = logging.getLogger("BABEL")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] BABEL: %(message)s")

gov = ImperialGovernance(
    entity_type="QUEEN", 
    entity_id=conf.QUEEN_ID,
    core_url=conf.CORE_URL, 
    gateway_token=conf.GATEWAY_TOKEN
)

# [UNIVERSAL KNOWLEDGE MAP] 영문/한글/유사어 통합 맵 (범용 확장 구조)
BABEL_MAP = {
    # FOOD DOMAIN
    "pork_belly": "BBL.ING.PORK_BELLY", 
    "pork belly": "BBL.ING.PORK_BELLY",
    "삼겹살": "BBL.ING.PORK_BELLY",
    "chicken_breast": "BBL.ING.CHICKEN_BREAST", 
    "chicken breast": "BBL.ING.CHICKEN_BREAST",
    "닭가슴살": "BBL.ING.CHICKEN_BREAST",
    "water": "BBL.NUT.WATER", 
    "물": "BBL.NUT.WATER",
    # CHEMICAL/MEDICAL PRE-SEED
    "ethanol": "BBL.CHM.ETHANOL", 
    "aspirin": "BBL.MED.ASPIRIN",
    "food": "BBL.ONT.FOOD",
    "recipes": "BBL.ONT.RECIPE",
    "recipe": "BBL.ONT.RECIPE",
    "chicken": "BBL.ING.CHICKEN",
    "pasta": "BBL.ING.PASTA"
}

def normalize_tag(tag: str) -> str:
    """비정형 태그 정규화: 소문자화, 특수문자 제거, 공백 정제"""
    if not tag: return ""
    # 영문 소문자화 및 한글/숫자/공백 제외 제거
    clean = re.sub(r'[^a-z0-9가-힣\s_]', '', tag.lower())
    return clean.strip()

@ensure_alive(gov)
async def knowledge_standardization_loop():
    """범용 지능 수확 루프: 비정형 태그 -> 표준 온톨로지 ID -> 지식 트리플 생성"""
    logger.info("[PROCESS] Babel Universal Engine V6.4 engaged.")
    while gov.is_alive:
        try:
            async with get_imperial_client() as client:
                # 1. AREUM 완료 자산 수확 (API: GET /v1/pipeline/assets/pending)
                res = await client.get(
                    f"{conf.CORE_URL}/pipeline/assets/pending?stratum_id={conf.STRATUM_ID}&limit=10",
                    headers=gov.headers
                )
                if res.status_code == 200:
                    assets = res.json().get("assets", [])
                    for asset in assets:
                        tags = asset.get("essence_tags", [])
                        triples = []
                        for raw_tag in tags:
                            norm_tag = normalize_tag(raw_tag)
                            # [SEMANTIC MATCHING] 정규화된 태그로 매핑 시도
                            if norm_tag in BABEL_MAP:
                                triples.append({
                                    "subject_id": BABEL_MAP[norm_tag],
                                    "predicate": "BBL.REL.REFERENCED_IN",
                                    "object_id": f"ASSET_{asset['id'][-8:]}",
                                    "confidence_score": asset.get("ai_confidence", 1.0)
                                })
                        
                        if triples:
                            # 2. 본토 지식그래프에 각인 (API: POST /v1/pipeline/knowledge/triples)
                            tx = await client.post(
                                f"{conf.CORE_URL}/pipeline/knowledge/triples",
                                json=triples,
                                headers=gov.headers
                            )
                            if tx.status_code == 200:
                                logger.info(f"[SUCCESS] Inscribed {len(triples)} knowledge triples for Asset {asset['id']}")
        except Exception as e:
            logger.error(f"[ERROR] Engine failure: {e}")
        await asyncio.sleep(60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # [SACRAMENT OF BIRTH]
    birth_data = {
        "queen_id": conf.QUEEN_ID,
        "queen_name": conf.QUEEN_NAME,
        "queen_type": "GENERAL",
        "relationship_type": "INTERNAL",
        "stratum_ids": [conf.STRATUM_ID],
        "host_ip": "127.0.0.1"
    }
    
    # 본체 파일의 절대 경로를 전달하여 레지스트리에 기록
    success = await gov.birth(payload=birth_data, instance_path=os.path.abspath(__file__))
    
    if success:
        await gov.start_heartbeat()
        task = asyncio.create_task(knowledge_standardization_loop())
        yield
        task.cancel()
        await gov.stop_heartbeat()
    else:
        logger.error("[CRITICAL] Birth Ceremony Failed. Check Core Connection.")
        yield

app = FastAPI(title="BABEL-QUEEN SOVEREIGN", version="9.0.0", lifespan=lifespan)

@app.get("/v1/babel/sync/export")
async def export_sovereign_knowledge():
    """[V9.0] 타 필드 전파를 위한 지식 덤프 추출"""
    return SovereignKnowledge.export_knowledge()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=conf.PORT_BABEL, reload=True)