import os
import asyncio
import asyncpg
from dotenv import load_dotenv

load_dotenv()

async def reconcile_db():
    print("=== COMMENCING DATABASE RECONCILIATION ===")
    conn = await asyncpg.connect(
        host=os.getenv('SUPABASE_HOST'),
        user=os.getenv('SUPABASE_USER'),
        password=os.getenv('SUPABASE_PASSWORD'),
        database=os.getenv('SUPABASE_DB'),
        port=os.getenv('SUPABASE_PORT')
    )
    
    PRIMARY_QUEEN_ID = 'ba537759-f607-4eda-841c-eeba65a5147b'
    STRATUM_ID = '3bb565af-e01a-49b8-af27-049e6a642f2d'
    
    async with conn.transaction():
        # 1. Demote all other queens
        await conn.execute('''
            UPDATE schema_registry.queens 
            SET status = 'CONSOLIDATED_MERGED' 
            WHERE queen_id != $1
        ''', PRIMARY_QUEEN_ID)
        print("  [OK] All other queens marked as CONSOLIDATED_MERGED.")
        
        # 2. Promote Primary Queen
        await conn.execute('''
            UPDATE schema_registry.queens 
            SET status = 'ACTIVE', stratum_ids = $2::uuid[] 
            WHERE queen_id = $1
        ''', PRIMARY_QUEEN_ID, [STRATUM_ID])
        print(f"  [OK] Queen {PRIMARY_QUEEN_ID} promoted to ACTIVE for Stratum {STRATUM_ID}.")
        
        # 3. Re-link AREUM entities
        await conn.execute('''
            UPDATE schema_registry.areums 
            SET queen_id = $1
        ''', PRIMARY_QUEEN_ID)
        print("  [OK] All AREUM entities re-linked to Primary Queen.")

    await conn.close()
    print("=== DATABASE RECONCILIATION COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(reconcile_db())
