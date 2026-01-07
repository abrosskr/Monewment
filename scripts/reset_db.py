
import asyncio
from sqlalchemy import text
from src.database import engine

async def reset_schema():
    async with engine.begin() as conn:
        print("🗑️ Dropping outdated tables...")
        await conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS projects CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS organizations CASCADE"))
        # Cluster might be new, so keep it or drop it too to be safe
        await conn.execute(text("DROP TABLE IF EXISTS clusters CASCADE"))
        print("✅ Tables dropped.")

if __name__ == "__main__":
    asyncio.run(reset_schema())
