import asyncio
from sqlalchemy import text
from core.database import engine
from datetime import datetime, timezone

async def register_stratum():
    async with engine.connect() as conn:
        sid = '3bb565af-e01a-49b8-af27-049e6a642f2d'
        print(f"Registering Stratum {sid}...")
        await conn.execute(text('''
            INSERT INTO schema_registry.stratums (stratum_id, stratum_name, status, born_at, root_path)
            VALUES (:sid, :name, :status, :born_at, :path)
            ON CONFLICT (stratum_id) DO UPDATE 
            SET status = 'ACTIVE'
        '''), {
            "sid": sid,
            "name": "PHYSICS-AREUM-CONSOLIDATED",
            "status": "ACTIVE",
            "born_at": datetime.now(timezone.utc),
            "path": "C:/monewment"
        })
        await conn.commit()
        print("  [OK] Stratum registered.")

if __name__ == "__main__":
    asyncio.run(register_stratum())
