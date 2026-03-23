import asyncio
import json
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

LOCAL_POSTGRES_URL = "postgresql+asyncpg://forager:forager@127.0.0.1:5432/forager"

async def deep_audit():
    engine = create_async_engine(LOCAL_POSTGRES_URL)
    async with engine.connect() as conn:
        print("--- [BOTTOM-UP] Physical Data Integrity Audit ---")
        
        # 1. areum_extraction Detailed Check
        res = await conn.execute(text("""
            SELECT e.asset_id, e.confidence_score, e.extracted_at, e.extracted_data
            FROM schema_stratum_stratum_1.areum_extraction e
            ORDER BY e.extracted_at DESC LIMIT 5
        """))
        extractions = res.fetchall()
        print(f"\n[EXTRACTION SAMPLES] Count: {len(extractions)}")
        for e in extractions:
            # Verify if extracted_data is valid JSON
            try:
                data = e.extracted_data
                if isinstance(data, str):
                    json.loads(data)
                print(f"  - Asset: {str(e.asset_id)[:8]} | Score: {e.confidence_score} | Time: {e.extracted_at}")
            except Exception as j_err:
                print(f"  [!!] JSON CORRUPTION DETECTED in Asset {e.asset_id}: {j_err}")

        # 2. Orphan Check (Assets with areum_processed_at but no extraction record)
        res = await conn.execute(text("""
            SELECT id FROM schema_stratum_stratum_1.assets 
            WHERE areum_processed_at IS NOT NULL 
            AND id NOT IN (SELECT asset_id FROM schema_stratum_stratum_1.areum_extraction)
        """))
        orphans = res.fetchall()
        print(f"\n[ORPHAN CHECK] Assets missing extraction records: {len(orphans)}")
        
        # 3. Registry vs Worker Check
        print("\n--- [TOP-DOWN] Architectural Alignment Audit ---")
        res = await conn.execute(text("SELECT ant_id, ant_name, status, last_seen_at FROM schema_registry.ants WHERE ant_type LIKE '%AREUM%'"))
        ants = res.fetchall()
        print(f"[WORKER REGISTRY] Detected AREUM Ants: {len(ants)}")
        for a in ants:
             print(f"  - {a.ant_name} | Status: {a.status} | Last Seen: {a.last_seen_at}")

if __name__ == "__main__":
    asyncio.run(deep_audit())
