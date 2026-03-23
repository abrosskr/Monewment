import asyncio
from sqlalchemy import text
from core.database import engine

async def find_ants():
    try:
        async with engine.connect() as conn:
            print("=== [ANTS] ===")
            q = text("SELECT ant_id, ant_name, ant_type, status FROM schema_registry.ants")
            res = await conn.execute(q)
            for r in res:
                print(f"Ant: {r.ant_name} | {r.ant_id} | {r.ant_type} | {r.status}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(find_ants())
