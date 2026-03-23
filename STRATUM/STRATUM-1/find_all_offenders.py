import asyncio
from sqlalchemy import text
from core.database import engine

async def find_all_offenders():
    try:
        async with engine.connect() as conn:
            # 1. Queens
            print("=== [QUEENS] ===")
            q = text("SELECT queen_id, queen_name, status FROM schema_registry.queens")
            res = await conn.execute(q)
            for r in res:
                print(f"Q: {r.queen_name} | {r.queen_id} | {r.status}")
            
            # 2. Areums
            print("\n=== [AREUMS] ===")
            q = text("SELECT areum_id, areum_name, status FROM schema_registry.areums")
            res = await conn.execute(q)
            for r in res:
                print(f"A: {r.areum_name} | {r.areum_id} | {r.status}")
                
            # 3. Tables search
            print("\n=== [TABLES] ===")
            q = text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'schema_registry'")
            res = await conn.execute(q)
            for r in res:
                print(f"Table: {r.table_name}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(find_all_offenders())
