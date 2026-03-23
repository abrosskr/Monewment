import asyncio
from sqlalchemy import text
from core.database import engine

async def implement_infinity():
    async with engine.connect() as conn:
        print("[IGNITION] Commencing Infinity Protocol Migration...")
        
        tables = [
            "schema_registry.monewments",
            "schema_registry.stratums",
            "schema_registry.queens",
            "schema_registry.ants"
        ]
        
        infinity_limit = 1000000000.0 # 1 Billion units
        
        for table in tables:
            print(f"[MIGRATION] Target: {table}")
            try:
                # 1. Update budget limit to Infinity
                # 2. Reset accumulated cost (Optional but clean)
                # 3. Revive any DEAD entities
                q = text(f"""
                    UPDATE {table} 
                    SET budget_limit = :lim, 
                        accumulated_cost = 0.0, 
                        status = 'ACTIVE' 
                    WHERE status != 'ACTIVE' OR budget_limit < :lim
                """)
                result = await conn.execute(q, {"lim": infinity_limit})
                print(f"[SUCCESS] {table}: {result.rowcount} rows upgraded to Infinity.")
            except Exception as e:
                print(f"[ERROR] {table} migration failed: {e}")
        
        await conn.commit()
        print("[FINISH] Infinity Protocol applied to all registry tables.")

if __name__ == "__main__":
    asyncio.run(implement_infinity())
