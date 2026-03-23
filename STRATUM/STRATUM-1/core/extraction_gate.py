import re
import json
import asyncio
import asyncpg
from core.logger import logger
from core.config import settings

# [IMPERIAL REGEX] - Zero Tolerance for Noise
AD_KEYWORDS_REGEX = re.compile(r"(판매|할인|쿠폰|구매|buy|sale|discount|click|ad)", re.IGNORECASE)
MIN_CONTENT_LENGTH = 100

async def structural_audit(asset_id: str, raw_text: str, db_url: str):
    """
    AREUM 수입 검사기 (The Structural Gatekeeper)
    글자 수, 광고 키워드, JSON 구조 파손 데이터를 'REJECTED' 상태로 즉시 분류함.
    """
    rejection_reason = None
    
    # 1. Length Guard
    if len(raw_text or "") < MIN_CONTENT_LENGTH:
        rejection_reason = f"INSUFFICIENT_LENGTH_({len(raw_text)})"
        
    # 2. Ad Noise Guard
    elif AD_KEYWORDS_REGEX.search(raw_text):
        rejection_reason = "AD_CONTAMINATION_DETECTED"
        
    # 3. JSON Integrity Guard (for nested metadata)
    try:
        if raw_text.strip().startswith('{') or raw_text.strip().startswith('['):
            json.loads(raw_text)
    except json.JSONDecodeError:
        rejection_reason = "MALFORMED_JSON_STRUCTURE"

    if rejection_reason:
        logger.warning(f"[GATEKEEPER] Asset {asset_id} REJECTED: {rejection_reason}")
        conn = await asyncpg.connect(db_url, statement_cache_size=0)
        try:
            # Physical Rejection SQL
            await conn.execute(f"""
                UPDATE schema_stratum_stratum_1.assets 
                SET pipeline_state = 'REJECTED', 
                    ai_summary = $1 
                WHERE id = $2
            """, rejection_reason, asset_id)
        finally:
            await conn.close()
        return False
    
    return True

if __name__ == "__main__":
    # Test Block
    print("[GATEKEEPER] Engine Armed.")
