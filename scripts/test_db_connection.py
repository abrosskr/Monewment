
import asyncio
from sqlalchemy import text
from src.database import engine

async def test_connection():
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(f"✅ DB Connection Success! Result: {result.scalar()}")
    except Exception as e:
        print(f"❌ DB Connection Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
