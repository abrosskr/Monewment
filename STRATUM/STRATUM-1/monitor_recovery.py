import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Use the environment-driven URL from config or hardcode for audit
LOCAL_POSTGRES_URL = "postgresql+asyncpg://forager:forager@127.0.0.1:5432/forager"

async def monitor():
    engine = create_async_engine(LOCAL_POSTGRES_URL)
    print("--- Real-time Recovery Monitor ---")
    while True:
        try:
            async with engine.connect() as conn:
                # 1. areum_extraction count
                res = await conn.execute(text("SELECT COUNT(*) FROM schema_stratum_stratum_1.areum_extraction"))
                extract_count = res.scalar()
                
                # 2. Latest asset processed
                res = await conn.execute(text("""
                    SELECT id, areum_processed_at 
                    FROM schema_stratum_stratum_1.assets 
                    WHERE areum_processed_at IS NOT NULL 
                    ORDER BY areum_processed_at DESC LIMIT 1
                """))
                latest = res.fetchone()
                
                print(f"[{asyncio.get_event_loop().time():.1f}] Extraction Count: {extract_count} | Latest: {latest}")
                
            if extract_count > 0:
                print("[SUCCESS] Live progress detected!")
                break
                
        except Exception as e:
            print(f"Monitor error: {e}")
            
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(monitor())
