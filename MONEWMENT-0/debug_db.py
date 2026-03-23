import asyncio
import os
from core.config import settings
from sqlalchemy import text
from core.database import engine

async def debug_db():
    print(f"[*] Core API Settings.SUPABASE_HOST: {settings.SUPABASE_HOST}")
    print(f"[*] Core API Settings.DATABASE_URL: {settings.DATABASE_URL}")
    
    try:
        async with engine.connect() as conn:
            res = await conn.execute(text("SELECT inet_server_addr(), current_database()"))
            addr, db_name = res.fetchone()
            print(f"[SUCCESS] Connected to: {addr} | DB: {db_name}")
            
            # Check Registry
            res = await conn.execute(text("SELECT COUNT(*) FROM schema_registry.ants"))
            print(f"[DATA] Ants in this DB: {res.scalar()}")
    except Exception as e:
        print(f"[CRITICAL ERR] Database connection failed: {e}")

if __name__ == "__main__":
    # Ensure we are in the right directory
    os.chdir("c:/monewment/MONEWMENT-0")
    asyncio.run(debug_db())
