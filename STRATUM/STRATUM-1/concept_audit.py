import asyncio, sys, os
from sqlalchemy import text
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.database import engine

async def check_missing_concepts():
    async with engine.connect() as conn:
        # Check current concepts
        res = await conn.execute(text("SELECT babel_id FROM schema_babel.concepts"))
        existing = {r[0] for r in res.fetchall()}
        
        # Concepts needed by inception loop (based on run_inception.py BABEL_MAP)
        needed = {
            "BBL.ING.BEEF", "BBL.ING.BACON", "BBL.ING.CHICKEN",
            "BBL.ING.PORK_BELLY", "BBL.ING.CHICKEN_BREAST", "BBL.NUT.WATER"
        }
        
        missing = needed - existing
        print(f"=== [CONCEPT AUDIT] ===")
        print(f" - Existing: {len(existing)}")
        print(f" - Missing: {missing}")

if __name__ == "__main__":
    asyncio.run(check_missing_concepts())
