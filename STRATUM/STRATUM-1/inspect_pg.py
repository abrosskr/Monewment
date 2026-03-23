import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def inspect_postgres():
    # Try 'forager' database
    url = "postgresql+asyncpg://forager:forager@127.0.0.1:5432/forager"
    engine = create_async_engine(url)
    try:
        async with engine.connect() as conn:
            print(f"--- [DATABASE: forager] ---")
            # 1. List Schemas
            res = await conn.execute(text("SELECT schema_name FROM information_schema.schemata"))
            schemas = [r[0] for r in res.fetchall()]
            print(f"SCHEMAS: {schemas}")
            
            # 2. Check schema_registry tables
            if 'schema_registry' in schemas:
                res = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'schema_registry'"))
                print(f"TABLES in schema_registry: {[r[0] for r in res.fetchall()]}")
                
                # Count ants
                res = await conn.execute(text("SELECT COUNT(*) FROM schema_registry.ants"))
                print(f"Ant Count: {res.scalar()}")
            else:
                print("schema_registry NOT FOUND in forager DB")
                
    except Exception as e:
        print(f"Error inspecting forager DB: {e}")

    # Try 'postgres' database
    url = "postgresql+asyncpg://forager:forager@127.0.0.1:5432/postgres"
    engine = create_async_engine(url)
    try:
        async with engine.connect() as conn:
            print(f"\n--- [DATABASE: postgres] ---")
            res = await conn.execute(text("SELECT schema_name FROM information_schema.schemata"))
            schemas = [r[0] for r in res.fetchall()]
            print(f"SCHEMAS: {schemas}")
            
            if 'schema_registry' in schemas:
                res = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'schema_registry'"))
                print(f"TABLES in schema_registry: {[r[0] for r in res.fetchall()]}")
                
                res = await conn.execute(text("SELECT COUNT(*) FROM schema_registry.ants"))
                print(f"Ant Count: {res.scalar()}")
    except Exception as e:
        print(f"Error inspecting postgres DB: {e}")

if __name__ == "__main__":
    asyncio.run(inspect_postgres())
