import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def crawl_postgres():
    # Connect to 'postgres' db to list others
    url = "postgresql+asyncpg://forager:forager@127.0.0.1:5432/postgres"
    engine = create_async_engine(url)
    try:
        async with engine.connect() as conn:
            print("--- [FULL CLUSTER AUDIT] ---")
            res = await conn.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false"))
            dbs = [r[0] for r in res.fetchall()]
            print(f"DATABASES FOUND: {dbs}")
            
            for db_name in dbs:
                print(f"\nScanning Database: {db_name}")
                db_url = f"postgresql+asyncpg://forager:forager@127.0.0.1:5432/{db_name}"
                db_engine = create_async_engine(db_url)
                try:
                    async with db_engine.connect() as db_conn:
                        res = await db_conn.execute(text("SELECT schema_name FROM information_schema.schemata"))
                        schemas = [r[0] for r in res.fetchall()]
                        print(f"  SCHEMAS: {schemas}")
                        if 'schema_registry' in schemas:
                            res = await db_conn.execute(text("SELECT COUNT(*) FROM schema_registry.ants"))
                            count = res.scalar()
                            print(f"  [REGISTRY DETECTED] Ants in {db_name}: {count}")
                            
                            # Give a sample to be sure
                            if count > 0:
                                res = await db_conn.execute(text("SELECT ant_name, ant_type, status FROM schema_registry.ants LIMIT 1"))
                                print(f"  SAMPLE: {res.fetchone()}")
                except Exception as e:
                    print(f"  Error scanning {db_name}: {e}")
    except Exception as e:
        print(f"Cluster audit failed: {e}")

if __name__ == "__main__":
    asyncio.run(crawl_postgres())
