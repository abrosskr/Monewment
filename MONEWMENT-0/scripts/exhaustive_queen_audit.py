import os
from pathlib import Path
from dotenv import load_dotenv
import asyncio
import asyncpg

load_dotenv()

async def audit():
    print("=== PHYSICAL DIRECTORY AUDIT ===")
    root = Path('C:/monewment')
    for d in ['PHYSICS', 'AREUM']:
        d_path = root / d
        if not d_path.exists(): continue
        for entry in d_path.iterdir():
            if entry.is_dir():
                env_file = entry / '.env'
                print(f"Directory: {entry}")
                if env_file.exists():
                    with open(env_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if any(k in line for k in ['STRATUM_ID', 'QUEEN_ID', 'NAME', 'AREUM_NAME', 'PHYSICS_NAME']):
                                print(f"  {line.strip()}")
                else:
                    print("  .env MISSING (Ghost Territory)")
    
    print("\n=== REGISTRY DATABASE AUDIT (ALL QUEENS) ===")
    conn = await asyncpg.connect(
        host=os.getenv('SUPABASE_HOST'),
        user=os.getenv('SUPABASE_USER'),
        password=os.getenv('SUPABASE_PASSWORD'),
        database=os.getenv('SUPABASE_DB'),
        port=os.getenv('SUPABASE_PORT')
    )
    
    rows = await conn.fetch('''
        SELECT queen_id, queen_name, stratum_ids, status, last_seen_at, born_at 
        FROM schema_registry.queens 
        ORDER BY born_at ASC
    ''')
    
    for r in rows:
        print(f"Queen: {r['queen_id']} | Name: {r['queen_name']} | Stratums: {r['stratum_ids']} | Status: {r['status']} | Born: {r['born_at']}")
        
    await conn.close()

if __name__ == "__main__":
    asyncio.run(audit())
