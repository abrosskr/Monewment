import asyncio, json, sys
from sqlalchemy import text
sys.path.append(r'C:\monewment\STRATUM\STRATUM-1')
from core.database import engine

async def audit():
    async with engine.connect() as conn:
        # 1. Concept Audit
        res_concepts = await conn.execute(text('SELECT babel_id FROM schema_babel.concepts'))
        concepts = [r[0] for r in res_concepts.fetchall()]
        
        # 2. Relation Audit
        res_relations = await conn.execute(text("SELECT * FROM schema_babel.concepts WHERE category = 'RELATION'"))
        relations = [dict(r._mapping) for r in res_relations.fetchall()]
        
        print(json.dumps({"concepts": concepts, "relations": relations}, default=str))

if __name__ == "__main__":
    asyncio.run(audit())
