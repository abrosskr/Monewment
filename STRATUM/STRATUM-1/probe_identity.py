# 🛰️ Imperial Identity Probe
# c:\monewment\STRATUM\STRATUM-1\probe_identity.py

import asyncio
from sqlalchemy import text
from core.database import AsyncSessionLocal

async def probe():
    ids_to_check = [
        ("areum", "66ca6a35-b894-46e5-93b2-354ffe3c8abf"),
        ("ant", "95d2c020-9ef7-4e01-9618-b17dd7ef0af1"),
        ("queen", "REX-CORE")
    ]
    
    async with AsyncSessionLocal() as db:
        for etype, eid in ids_to_check:
            table = f"schema_registry.{etype}s"
            id_col = f"{etype}_id"
            try:
                q = text(f"SELECT * FROM {table} WHERE {id_col}::text = :eid")
                res = await db.execute(q, {"eid": eid})
                row = res.fetchone()
                if row:
                    print(f"[OK] {etype} {eid} FOUND in {table}")
                else:
                    print(f"[MISSING] {etype} {eid} NOT FOUND in {table}")
                    # Check if it exists with a DIFFERENT ID?
                    q2 = text(f"SELECT {id_col}::text FROM {table} LIMIT 5")
                    res2 = await db.execute(q2)
                    others = [r[0] for r in res2.fetchall()]
                    print(f"    Existing {etype} IDs: {others}")
            except Exception as e:
                print(f"[ERROR] Testing {etype}: {e}")

if __name__ == "__main__":
    asyncio.run(probe())
