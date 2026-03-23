import asyncio
from sqlalchemy import text
from core.database import engine

async def inspect_budgets():
    async with engine.connect() as conn:
        tables = [
            ("schema_registry.monewments", "monewment_id", "display_name"),
            ("schema_registry.stratums", "stratum_id", "stratum_name"),
            ("schema_registry.queens", "queen_id", "queen_name"),
            ("schema_registry.ants", "ant_id", "ant_name"),
        ]
        
        print(f"{'Table':<25} | {'ID':<36} | {'Name':<20} | {'AccCost':<12} | {'Limit':<12} | {'Status':<8}")
        print("-" * 125)
        
        for table, id_col, name_col in tables:
            try:
                q = text(f"SELECT {id_col}, {name_col}, accumulated_cost, budget_limit, status FROM {table} WHERE status = 'ACTIVE' OR {name_col} LIKE '%PHYSICS%'")
                result = await conn.execute(q)
                rows = result.fetchall()
                for row in rows:
                    acc_cost = row[2] if row[2] is not None else 0.0
                    lim = row[3] if row[3] is not None else 0.0
                    print(f"{table:<25} | {str(row[0]):<36} | {str(row[1]):<20} | {acc_cost:<12.2f} | {lim:<12.2f} | {row[4]:<8}")
            except Exception as e:
                print(f"Error querying {table}: {e}")

if __name__ == "__main__":
    asyncio.run(inspect_budgets())
