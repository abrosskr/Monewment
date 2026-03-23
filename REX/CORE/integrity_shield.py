import asyncio
import asyncpg
import re
from core.logger import logger

# [MEDICAL & NUTRITIONAL CONSTANTS] - Imperial Truth Base
MEDICAL_CONSTANTS = {
    "MIN_CALORIES_PER_100G": 0.0, # Negative calories is a hallucination
    "MAX_PROTEIN_PER_100G": 100.0,
    "MIN_CONFIDENCE_THRESHOLD": 0.8
}

async def integrity_shield(triple_id: str, subject_id: str, predicate: str, object_id: str, confidence: float, db_url: str):
    """
    REX 지능 검문소 (The Semantic Gatekeeper)
    """
    logger.info(f"[SHIELD] Auditing Triple {triple_id}: {predicate} = {object_id} (Conf: {confidence})")
    quarantine_reason = None
    
    # 1. Confidence Threshold
    if confidence < MEDICAL_CONSTANTS["MIN_CONFIDENCE_THRESHOLD"]:
        quarantine_reason = f"LOW_CONFIDENCE_({confidence})"
        
    # 2. Semantic Contradiction
    if "CALORIE" in predicate.upper():
        numeric_part = re.findall(r"-?\d+\.?\d*", object_id)
        if numeric_part:
            val = float(numeric_part[0])
            logger.info(f"[SHIELD] Extracted Calorie Value: {val}")
            if val < MEDICAL_CONSTANTS["MIN_CALORIES_PER_100G"]:
                quarantine_reason = f"SEMANTIC_CONTRADICTION_NEG_CAL_({val})"

    if quarantine_reason:
        logger.error(f"[SHIELD] Triple {triple_id} QUARANTINED: {quarantine_reason}")
        conn = await asyncpg.connect(db_url, statement_cache_size=0)
        try:
            # Transfer to Quarantine Logic (Simulated by pipeline_state)
            await conn.execute("""
                UPDATE schema_babel.knowledge_triples 
                SET confidence_score = -1.0, 
                    predicate = 'QUARANTINE:' || predicate
                WHERE triple_id = $1
            """, triple_id)
        finally:
            await conn.close()
        return False
        
    return True

if __name__ == "__main__":
    print("[SHIELD] Semantic Sentinel Online.")
