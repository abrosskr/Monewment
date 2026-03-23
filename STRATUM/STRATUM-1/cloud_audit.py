import asyncio
import json
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Supabase Credentials from MONEWMENT-0/.env
SUPABASE_URL = "postgresql+asyncpg://postgres.vtcwsehwbyzpjuirviir:gmlwkTltkfkdgo123@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

async def cloud_audit():
    # Force transaction mode compliance
    engine = create_async_engine(
        SUPABASE_URL,
        connect_args={
            "prepared_statement_cache_size": 0,
            "statement_cache_size": 0,
        }
    )
    async with engine.connect() as conn:
        print("--- [CLOUD AUDIT] Supabase Integrity Check ---")
        
        # 1. Extraction Count in Supabase
        try:
            res = await conn.execute(text("SELECT COUNT(*) FROM schema_stratum_stratum_1.areum_extraction"))
            count = res.scalar()
            print(f"[CLOUD] Total Extractions: {count}")
        except Exception as e:
            print(f"[CLOUD ERR] scan areum_extraction failed: {e}")

        # 2. Registry Check in Supabase
        try:
            res = await conn.execute(text("SELECT COUNT(*) FROM schema_registry.ants WHERE ant_type LIKE '%AREUM%'"))
            ant_count = res.scalar()
            print(f"[CLOUD] Registered AREUM Ants: {ant_count}")
        except Exception as e:
            print(f"[CLOUD ERR] scan ants failed: {e}")

if __name__ == "__main__":
    asyncio.run(cloud_audit())
