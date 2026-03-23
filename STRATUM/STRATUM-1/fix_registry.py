import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

LOCAL_POSTGRES_URL = "postgresql+asyncpg://forager:forager@127.0.0.1:5432/forager"

async def fix():
    engine = create_async_engine(LOCAL_POSTGRES_URL)
    async with engine.begin() as conn:
        print("[*] Restoring Imperial Registry Integrity...")
        
        # 1. Restore Monewment
        await conn.execute(text("""
            INSERT INTO schema_registry.monewments (monewment_id, display_name, owner_user_id)
            VALUES ('d8a9e0a0-0000-0000-0000-000000000000', 'IMPERIAL_CORE', 'SYSTEM')
            ON CONFLICT (monewment_id) DO NOTHING
        """))
        
        # 2. Restore Queen
        await conn.execute(text("""
            INSERT INTO schema_registry.queens (queen_id, queen_name, relationship_type, queen_type)
            VALUES ('e5388cf9-4ce2-400e-8de1-f9e2a5bb18bd', 'QUEEN-SFIS', 'INTERNAL', 'FORAGER')
            ON CONFLICT (queen_id) DO NOTHING
        """))
        
        print("[OK] Registry Restoration Complete.")

if __name__ == "__main__":
    asyncio.run(fix())
