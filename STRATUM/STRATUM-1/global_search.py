import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

LOCAL_POSTGRES_URL = "postgresql+asyncpg://forager:forager@127.0.0.1:5432/forager"

async def audit():
    engine = create_async_engine(LOCAL_POSTGRES_URL)
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'schema_%'"))
        schemas = [r[0] for r in res.fetchall()]
        
        print("--- Global Data Search ---")
        for schema in schemas:
            try:
                # Check for assets table
                res = await conn.execute(text(f"SELECT COUNT(*) FROM {schema}.assets"))
                count = res.scalar()
                if count > 0:
                    print(f"[FOUND] {schema}.assets: {count}")
                
                # Check for target_sites table
                res = await conn.execute(text(f"SELECT COUNT(*) FROM {schema}.target_sites"))
                t_count = res.scalar()
                if t_count > 0:
                    print(f"[FOUND] {schema}.target_sites: {t_count}")
            except:
                pass

if __name__ == "__main__":
    asyncio.run(audit())
