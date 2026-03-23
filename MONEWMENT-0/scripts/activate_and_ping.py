import asyncio
from sqlalchemy import text
from core.database import engine

async def activate_and_ping():
    print("Activating and Pinging all key entities...")
    stratums = [
        "604c3454-88c5-4c27-8033-a7f5d548ad2b", # recilabel
        "92d47afe-fa95-465a-9159-37fd4631b227", # sfis
        "a8527246-b140-42cf-b304-00f4587ee1f4"  # STRATUM_1
    ]
    async with engine.connect() as conn:
        # 1. Activate Stratums
        for sid in stratums:
            await conn.execute(text("""
                UPDATE schema_registry.stratums 
                SET status = 'ACTIVE', last_seen_at = NOW()
                WHERE stratum_id = CAST(:sid AS UUID)
            """), {"sid": sid})
        
        # 2. Activate Queens
        await conn.execute(text("""
            UPDATE schema_registry.queens 
            SET status = 'ACTIVE', last_seen_at = NOW()
            WHERE status != 'ACTIVE'
        """))
        
        await conn.commit()
        print("  All key entities set to ACTIVE and PINGED.")

if __name__ == "__main__":
    asyncio.run(activate_and_ping())
