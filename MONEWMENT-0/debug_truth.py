import asyncio
import os
from core.config import settings
from sqlalchemy import text
from core.database import engine

async def debug_truth():
    print("--- [ENVIRONMENT AUDIT] ---")
    for k in ["SUPABASE_HOST", "SUPABASE_PORT", "SUPABASE_DB", "SUPABASE_USER"]:
        print(f"{k}: {os.environ.get(k, 'NOT_SET')}")
    
    print("\n--- [SETTINGS AUDIT] ---")
    print(f"settings.SUPABASE_HOST: {settings.SUPABASE_HOST}")
    print(f"settings.DATABASE_URL: {settings.DATABASE_URL}")
    
    print("\n--- [SESSION AUDIT] ---")
    try:
        async with engine.connect() as conn:
            res = await conn.execute(text("SELECT inet_server_addr(), current_database(), current_user"))
            addr, db_name, user = res.fetchone()
            print(f"CONNECTED TO: {addr} | DB: {db_name} | USER: {user}")
            
            # Check for ANY registered ants
            res = await conn.execute(text("SELECT COUNT(*) FROM schema_registry.ants"))
            print(f"ANTS IN THIS SESSION: {res.scalar()}")
            
            # Check for ANY sequences
            res = await conn.execute(text("SELECT entity_class, current_value FROM schema_registry.sequences"))
            rows = res.fetchall()
            for r in rows:
                 if r[1] > 1:
                     print(f"ACTIVE SEQUENCE: {r[0]} = {r[1]}")
    except Exception as e:
        print(f"DEBUG FAIL: {e}")

if __name__ == "__main__":
    os.chdir("c:/monewment/MONEWMENT-0")
    asyncio.run(debug_truth())
