import asyncio
from sqlalchemy import text
from core.database import engine

async def find_offenders():
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
                # Direct check for offenders
                q = text(f"SELECT {id_col}, {name_col}, accumulated_cost, budget_limit, status FROM {table} WHERE accumulated_cost > budget_limit")
                result = await conn.execute(q)
                rows = result.fetchall()
                for row in rows:
                    print(f"{table:<25} | {str(row[0]):<36} | {str(row[1]):<20} | {row[2]:<12.2f} | {row[3]:<12.2f} | {row[4]:<8}")
                
                # Also check for those with very low limits (like the old 5.0)
                q2 = text(f"SELECT {id_col}, {name_col}, accumulated_cost, budget_limit, status FROM {table} WHERE budget_limit < 100")
                result2 = await conn.execute(q2)
                rows2 = result2.fetchall()
                for row in rows2:
                    print(f"[LOW_LIM] {table:<25} | {str(row[0]):<36} | {str(row[1]):<20} | {row[2]:<12.2f} | {row[3]:<12.2f} | {row[4]:<8}")
                    
            except Exception as e:
                print(f"Error querying {table}: {e}")

if __name__ == "__main__":
    asyncio.run(find_offenders())
