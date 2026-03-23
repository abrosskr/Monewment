import asyncio, sys, os
from sqlalchemy import text
sys.path.append(os.path.abspath('.'))
from core.database import engine

async def get_count():
    try:
        async with engine.connect() as conn:
            res = await conn.execute(text("SELECT count(*) FROM schema_babel.knowledge_triples WHERE source_queen_id IS NOT NULL"))
            count = res.scalar()
            print("\n" + "="*40)
            print(f"[IMPERIAL REPORT] 현재 각인된 실전 지식 수: {count}개")
            print("="*40 + "\n")
    except Exception as e:
        print(f"\n[ERROR] DB 접속 실패: {e}")

if __name__ == '__main__':
    asyncio.run(get_count())
