
import asyncio
from sqlalchemy import text
from core.database import engine

async def run():
    async with engine.begin() as conn:
        print("EXECUTING RAW REX FEED TEMPORAL PURGE (NO FILTER)...")
        # [TEMPORAL PURGE] 4시간 필터 제거하여 08시 데이터를 17시로 강제 이동
        await conn.execute(text("""
            UPDATE schema_pipeline.strategic_decrees 
            SET rex_consumed_at = rex_consumed_at + INTERVAL '9 hours' 
            WHERE rex_consumed = TRUE
        """))
        r = await conn.execute(text("SELECT decree_id, rex_consumed_at FROM schema_pipeline.strategic_decrees WHERE rex_consumed = TRUE LIMIT 5"))
        print(f"FEED_SYNC_VAL: {r.fetchall()}")

if __name__ == "__main__":
    asyncio.run(run())
