import asyncio, json, sys
from sqlalchemy import text
sys.path.append(r'C:\monewment\STRATUM\STRATUM-1')
from core.database import engine

async def audit():
    async with engine.connect() as conn:
        res = await conn.execute(text('SELECT source_queen_id, created_at FROM schema_babel.knowledge_triples WHERE source_queen_id IS NOT NULL ORDER BY created_at DESC LIMIT 5'))
        rows = [dict(r._mapping) for r in res.fetchall()]
        print(json.dumps(rows, default=str))

if __name__ == "__main__":
    asyncio.run(audit())
