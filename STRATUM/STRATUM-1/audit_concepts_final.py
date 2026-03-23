import asyncio, sys, os
from sqlalchemy import text

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.database import engine

async def audit_concepts():
    try:
        async with engine.connect() as conn:
            res = await conn.execute(text("SELECT babel_id, canonical_name FROM schema_babel.concepts LIMIT 50"))
            print("=== [KNOWLEDGE REGISTRY AUDIT] ===")
            for r in res.fetchall():
                print(f" - {r[0]}: {r[1]}")
    except Exception as e:
        print(f"[CRITICAL] Concept audit failed: {e}")

if __name__ == "__main__":
    asyncio.run(audit_concepts())
