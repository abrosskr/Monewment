import asyncio, sys, json
sys.path.append('.')
from core.database import AsyncSessionLocal
from sqlalchemy import text

async def check():
    aid = 'e6581089-9c09-42f4-92bf-a1e27da9b121' # From last user log
    async with AsyncSessionLocal() as s:
        print('--- AREUM Worker In Ants Table ---')
        r = await s.execute(text('SELECT ant_id, ant_name, fencing_token FROM schema_registry.ants WHERE ant_id = CAST(:aid AS uuid)'), {'aid': aid})
        row = r.fetchone()
        print(f'DB Info: {row}')
        
        print('\n--- areum_extraction Columns & Defaults ---')
        r2 = await s.execute(text("""
            SELECT column_name, column_default, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'schema_stratum_stratum_1' AND table_name = 'areum_extraction'
        """))
        for c in r2.all():
            print(c)

        print('\n--- is strategic_decrees table exists? ---')
        r3 = await s.execute(text("""
            SELECT count(*) FROM information_schema.tables 
            WHERE table_schema = 'schema_stratum_stratum_1' AND table_name = 'strategic_decrees'
        """))
        print(f'strategic_decrees count: {r3.scalar()}')

asyncio.run(check())
