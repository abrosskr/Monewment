import asyncio
from core.database import AsyncSessionLocal
from sqlalchemy import text
import json

async def check():
    async with AsyncSessionLocal() as db:
        results = {}
        for table in ['ants', 'queens', 'areums']:
            id_col = f"{table[:-1]}_id"
            name_col = f"{table[:-1]}_name"
            res = await db.execute(text(f"SELECT {id_col}, {name_col}, last_seen_at FROM schema_registry.{table} WHERE status = 'ACTIVE'"))
            results[table] = [dict(row._mapping) for row in res]
        
        # Convert types to string for JSON serialization
        class CustomEncoder(json.JSONEncoder):
            def default(self, obj):
                if hasattr(obj, 'isoformat'):
                    return obj.isoformat()
                import uuid
                if isinstance(obj, uuid.UUID):
                    return str(obj)
                return super().default(obj)

        print(json.dumps(results, indent=2, cls=CustomEncoder))

if __name__ == "__main__":
    asyncio.run(check())
