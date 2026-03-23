import asyncio
from sqlalchemy import text
from core.database import engine

async def activate_all():
    print("Force activating all relevant stratums and queens...")
    async with engine.connect() as conn:
        # Update stratums
        res_s = await conn.execute(text("""
            UPDATE schema_registry.stratums 
            SET status = 'ACTIVE' 
            WHERE stratum_name ILIKE '%forager%' 
               OR stratum_name ILIKE '%recilabel%' 
               OR stratum_name ILIKE '%physics%' 
               OR stratum_name ILIKE '%sfis%'
               OR stratum_name = 'STRATUM-1'
               OR stratum_name = 'STRATUM_1'
            RETURNING stratum_name
        """))
        print(f"Stratums activated: {[r[0] for r in res_s.fetchall()]}")

        # Update queens
        res_q = await conn.execute(text("""
            UPDATE schema_registry.queens 
            SET status = 'ACTIVE' 
            WHERE queen_name ILIKE '%forager%' 
               OR queen_name ILIKE '%labeller%' 
               OR queen_name ILIKE '%physics%' 
               OR queen_name ILIKE '%sfis%' 
               OR queen_name ILIKE '%recilabeler%'
            RETURNING queen_name
        """))
        print(f"Queens activated: {[r[0] for r in res_q.fetchall()]}")
        
        await conn.commit()

if __name__ == "__main__":
    asyncio.run(activate_all())
