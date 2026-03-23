import asyncio
from core.database import AsyncSessionLocal
from sqlalchemy import text

async def main():
    async with AsyncSessionLocal() as db:
        # AREUM-1
        await db.execute(text("UPDATE schema_registry.areums SET instance_path = 'C:\\monewment\\AREUM\\AREUM-1' WHERE status = 'ACTIVE'"))
        # PHYSICS-1
        await db.execute(text("UPDATE schema_registry.ants SET instance_path = 'C:\\monewment\\PHYSICS\\PHYSICS-1' WHERE status = 'ACTIVE'"))
        await db.commit()
        print("Golden seeds planted successfully.")

if __name__ == "__main__":
    asyncio.run(main())
