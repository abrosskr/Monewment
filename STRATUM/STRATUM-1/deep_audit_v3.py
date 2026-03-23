import asyncio
import json
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

LOCAL_POSTGRES_URL = "postgresql+asyncpg://forager:forager@127.0.0.1:5432/forager"

async def deep_audit_v3():
    engine = create_async_engine(LOCAL_POSTGRES_URL)
    async with engine.connect() as conn:
        print("--- [DEEP AUDIT V3] Imperial Integrity Check ---")
        
        # 1. Physical Extraction Count
        res = await conn.execute(text("SELECT COUNT(*) FROM schema_stratum_stratum_1.areum_extraction"))
        count = res.scalar()
        print(f"[BOTTOM-UP] Total Extractions: {count}")
        
        # 2. Registry Dump (Everything in schema_registry.ants)
        print("\n--- [REGISTRY] Full 'ants' Table Dump ---")
        res = await conn.execute(text("SELECT ant_id, ant_name, ant_type, status, last_seen_at, born_at FROM schema_registry.ants"))
        ants = res.fetchall()
        print(f"Total Ants Registered: {len(ants)}")
        for a in ants:
            print(f"  - ID: {a.ant_id} | Name: {a.ant_name} | Type: {a.ant_type} | Status: {a.status} | LastSeen: {a.last_seen_at}")
            
        # 3. Registry Dump (Everything in schema_registry.queens)
        print("\n--- [REGISTRY] Full 'queens' Table Dump ---")
        res = await conn.execute(text("SELECT queen_id, queen_name, relationship_type, status FROM schema_registry.queens"))
        queens = res.fetchall()
        for q in queens:
            print(f"  - ID: {q.queen_id} | Name: {q.queen_name} | Rel: {q.relationship_type} | Status: {q.status}")

        # 4. Check for 'STANDALONE' records in areum_extraction (if any)
        # Assuming asset_id is UUID, but maybe workers are reporting a different way?
        # Actually asset_id is FK to assets.
        
if __name__ == "__main__":
    asyncio.run(deep_audit_v3())
