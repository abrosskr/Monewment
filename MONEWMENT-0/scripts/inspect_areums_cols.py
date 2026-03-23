import os
import asyncio
import asyncpg
from dotenv import load_dotenv

load_dotenv()

async def inspect():
    conn = await asyncpg.connect(
        host=os.getenv('SUPABASE_HOST'),
        user=os.getenv('SUPABASE_USER'),
        password=os.getenv('SUPABASE_PASSWORD'),
        database=os.getenv('SUPABASE_DB'),
        port=os.getenv('SUPABASE_PORT')
    )
    
    rows = await conn.fetch('''
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'schema_registry' 
        AND table_name = 'areums'
    ''')
    
    for row in rows:
        print(f"Column: {row['column_name']}, Type: {row['data_type']}")
        
    await conn.close()

if __name__ == "__main__":
    asyncio.run(inspect())
