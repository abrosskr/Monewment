import asyncio
from core.database import AsyncSessionLocal
from sqlalchemy import text

async def main():
    async with AsyncSessionLocal() as db:
        # STRATUM-1
        await db.execute(text("""
            INSERT INTO schema_registry.stratums (stratum_id, stratum_name, monewment_id, root_path, status)
            VALUES ('3bb565af-e01a-49b8-af27-049e6a642f2d', 'stratum_1', '769f37c4-f203-455b-9d41-e940e793e25d', 'C:\\monewment\\STRATUM\\STRATUM-1', 'ACTIVE')
            ON CONFLICT (stratum_id) DO UPDATE SET status = 'ACTIVE'
        """))
        # GOLDEN QUEEN
        await db.execute(text("""
            INSERT INTO schema_registry.queens (queen_id, queen_name, relationship_type, queen_type, status, instance_path)
            VALUES ('ba537759-f607-4eda-841c-eeba65a5147b', 'QUEEN-IN-68', 'INTERNAL', 'GENERAL', 'ACTIVE', 'C:\\monewment\\MONEWMENT-0')
            ON CONFLICT (queen_id) DO UPDATE SET status = 'ACTIVE', instance_path = 'C:\\monewment\\MONEWMENT-0'
        """))
        await db.commit()
        print("Golden Infrastructure Restored.")

if __name__ == "__main__":
    asyncio.run(main())
