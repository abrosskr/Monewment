import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from core.config import settings

async def provision_and_seed():
    # Run the core provisioner methods
    try:
        from core.provisioner import Provisioner
        from core.database import engine
        
        await Provisioner.create_registry_space()
        await Provisioner.create_pipeline_space()
        await Provisioner.create_stratum_space("forager_crawl")
        
        async with engine.begin() as conn:
            # Seed the default MONEWMENT mapping
            monewment_id = "11111111-1111-1111-1111-111111111111"
            await conn.execute(text(f"""
                INSERT INTO schema_registry.monewments (monewment_id, display_name, owner_user_id)
                VALUES ('{monewment_id}', 'MONEWMENT-1', 'system')
                ON CONFLICT (monewment_id) DO NOTHING;
            """))
            
            # Seed STRATUM-1 mapping (forager_crawl)
            stratum_id = "badd8a15-5e63-4d24-81fd-489e8973cb85"
            await conn.execute(text(f"""
                INSERT INTO schema_registry.stratums (stratum_id, stratum_name, monewment_id)
                VALUES ('{stratum_id}', 'forager_crawl', '{monewment_id}')
                ON CONFLICT (stratum_id) DO UPDATE 
                SET stratum_name = 'forager_crawl';
            """))
            
            print(f"[+] Provisioning & Seeding complete. STRATUM_ID: {stratum_id} mapped to 'forager_crawl'")
            
    except Exception as e:
        print(f"Failed to provision: {e}")

if __name__ == "__main__":
    asyncio.run(provision_and_seed())
