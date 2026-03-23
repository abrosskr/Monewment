import asyncio
from sqlalchemy import text
from core.database import engine

async def check():
    async with engine.connect() as conn:
        s1_schema = "schema_stratum_stratum_1"
        
        # 1. Total assets and processed status
        res = await conn.execute(text(f"SELECT COUNT(*), COUNT(areum_id), COUNT(rex_processed_at) FROM {s1_schema}.assets"))
        total, areum_proc, rex_proc = res.fetchone()
        print(f"ASSETS: Total={total}, AREUM_Proc={areum_proc}, REX_Proc={rex_proc}")
        
        # 2. areum_extraction table
        res = await conn.execute(text(f"SELECT COUNT(*) FROM {s1_schema}.areum_extraction"))
        ext_count = res.fetchone()[0]
        print(f"EXTRACTION: {ext_count}")
        
        # 3. Pipeline cross reports
        res = await conn.execute(text("SELECT COUNT(*) FROM schema_pipeline.cross_reports WHERE stratum_id = 'a8527246-b140-42cf-b304-00f4587ee1f4'"))
        cross_count = res.fetchone()[0]
        print(f"CROSS_REPORTS: {cross_count}")
        
        # 4. REX Learning Queue
        res = await conn.execute(text("SELECT status, COUNT(*) FROM schema_rex.learning_queue GROUP BY status"))
        rex_q = res.fetchall()
        print(f"REX_QUEUE: {rex_q}")

if __name__ == '__main__':
    asyncio.run(check())
