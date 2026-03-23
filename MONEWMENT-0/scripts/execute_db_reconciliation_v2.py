import os
import asyncio
import asyncpg
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

async def execute_full_reconciliation():
    print("=== COMMENCING ATOMIC DATABASE RECONCILIATION ===")
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
        # 1. Ensure Primary Queen Exists (Manual Birth)
        await conn.execute('''
            INSERT INTO schema_registry.queens (queen_id, queen_name, status, born_at, stratum_ids)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (queen_id) DO UPDATE 
            SET status = 'ACTIVE', stratum_ids = $5
        ''', PRIMARY_QUEEN_ID, 'PHYSICS-QUEEN-SUPREME', 'ACTIVE', datetime.now(timezone.utc), [STRATUM_ID])
        print(f"  [OK] Primary Queen {PRIMARY_QUEEN_ID} Birthed/Activated.")

        # 2. Demote ALL OTHER active queens to CONSOLIDATED_MERGED
        await conn.execute('''
            UPDATE schema_registry.queens 
            SET status = 'CONSOLIDATED_MERGED' 
            WHERE queen_id != $1 AND status != 'DIED'
        ''', PRIMARY_QUEEN_ID)
        print("  [OK] All other active queens consolidated.")
        
        # 3. Re-link ALL AREUM entities to the Supreme Queen
        await conn.execute('''
            UPDATE schema_registry.areums 
            SET queen_id = $1
        ''', PRIMARY_QUEEN_ID)
        print("  [OK] All AREUM entities re-linked.")

    await conn.close()
    print("=== DATABASE RECONCILIATION COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(execute_full_reconciliation())
