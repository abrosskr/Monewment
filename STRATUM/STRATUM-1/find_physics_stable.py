import asyncio
from sqlalchemy import text
from core.database import engine

async def find_physics_stable():
    async with engine.connect() as conn:
        q = text("""
            SELECT queen_id, queen_name, accumulated_cost, budget_limit, status, death_reason 
            FROM schema_registry.queens 
            WHERE queen_name = 'QUEEN-IN-PHYSICS-STABLE-001'
        """)
        result = await conn.execute(q)
        row = result.fetchone()
        if row:
            print("--- FOUND STABLE PHYSICS QUEEN ---")
            print(f"ID: {row[0]}")
            print(f"Name: {row[1]}")
            print(f"AccCost: {row[2]}")
            print(f"Limit: {row[3]}")
            print(f"Status: {row[4]}")
            print(f"DeathReason: {row[5]}")
        else:
            print("--- STABLE PHYSICS QUEEN NOT FOUND ---")
            # Let's check if there's any queen with this ID as a string in the queen_id column (if castable)
            # or just any queen at all again.
            q2 = text("SELECT count(*) FROM schema_registry.queens")
            res2 = await conn.execute(q2)
            print(f"Total Queens in DB: {res2.scalar()}")

if __name__ == "__main__":
    asyncio.run(find_physics_stable())
