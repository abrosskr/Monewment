import asyncio
from sqlalchemy import text
from core.database import engine

async def reset():
    async with engine.connect() as conn:
        print("Resetting budget for fe6674a6-4e51-4c4c-83cd-b17d52fa0989...")
        await conn.execute(text("""
            UPDATE schema_registry.ants 
            SET accumulated_cost = 0.0, 
                status = 'ACTIVE', 
                budget_limit = 1000.0, 
                died_at = NULL, 
                death_reason = NULL 
            WHERE ant_id = 'fe6674a6-4e51-4c4c-83cd-b17d52fa0989'
        """))
        await conn.commit()
        print("Done.")

if __name__ == "__main__":
    asyncio.run(reset())
