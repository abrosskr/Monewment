import asyncio
from sqlalchemy import text
from core.database import engine

async def activate_stratums_force():
    print("Force activating key stratums...")
    stratums = [
        "604c3454-88c5-4c27-8033-a7f5d548ad2b", # recilabel
        "92d47afe-fa95-465a-9159-37fd4631b227", # sfis
        "a8527246-b140-42cf-b304-00f4587ee1f4"  # STRATUM_1
    ]
    async with engine.connect() as conn:
        for sid in stratums:
            result = await conn.execute(text("""
                UPDATE schema_registry.stratums 
                SET status = 'ACTIVE' 
                WHERE stratum_id = CAST(:sid AS UUID)
            """), {"sid": sid})
            await conn.commit()
            print(f"  Stratum {sid} set to ACTIVE. Rows affected: {result.rowcount}")

        # Verify immediately
        res = await conn.execute(text("SELECT stratum_name, status FROM schema_registry.stratums WHERE stratum_id IN (CAST('604c3454-88c5-4c27-8033-a7f5d548ad2b' AS uuid), CAST('92d47afe-fa95-465a-9159-37fd4631b227' AS uuid), CAST('a8527246-b140-42cf-b304-00f4587ee1f4' AS uuid))"))
        for r in res.fetchall():
            print(f"  VERIFY: {r.stratum_name} -> {r.status}")

if __name__ == "__main__":
    asyncio.run(activate_stratums_force())
