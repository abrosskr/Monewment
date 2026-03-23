import asyncio
from sqlalchemy import text
from core.database import engine

async def activate_stratums():
    print("Activating key stratums for ecosystem check...")
    stratums = [
        "604c3454-88c5-4c27-8033-a7f5d548ad2b", # recilabel
        "92d47afe-fa95-465a-9159-37fd4631b227", # sfis
        "a8527246-b140-42cf-b304-00f4587ee1f4"  # STRATUM-1 (EDENVALE)
    ]
    async with engine.begin() as conn:
        for sid in stratums:
            await conn.execute(text("UPDATE schema_registry.stratums SET status = 'ACTIVE' WHERE stratum_id = :sid"), {"sid": sid})
            print(f"  Stratum {sid} set to ACTIVE.")

if __name__ == "__main__":
    asyncio.run(activate_stratums())
