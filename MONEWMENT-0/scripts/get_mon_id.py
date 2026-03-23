import asyncio
from sqlalchemy import text
from core.database import engine

async def get_mon():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT monewment_id FROM schema_registry.monewments LIMIT 1"))
        print(res.scalar())

if __name__ == "__main__":
    asyncio.run(get_mon())
