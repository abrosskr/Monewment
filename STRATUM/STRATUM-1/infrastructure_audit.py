import asyncio
import sys
import os
from sqlalchemy import text
from core.database import AsyncSessionLocal

async def get_hard_facts():
    async with AsyncSessionLocal() as db:
        print("[FACT] --- DB PHYSICAL STRUCTURE: cross_reports ---")
        q1 = text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_schema = 'schema_pipeline' AND table_name = 'cross_reports'
            ORDER BY ordinal_position;
        """)
        res1 = await db.execute(q1)
        for row in res1.fetchall():
            print(f"Col: {row[0]}, Type: {row[1]}, Nullable: {row[2]}, Default: {row[3]}")

        print("\n[FACT] --- DB PHYSICAL STRUCTURE: stratums ---")
        q2 = text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'schema_registry' AND table_name = 'stratums' AND column_name = 'stratum_id';
        """)
        res2 = await db.execute(q2)
        for row in res2.fetchall():
            print(f"Col: {row[0]}, Type: {row[1]}")

        q3 = text("SELECT stratum_id, stratum_name FROM schema_registry.stratums LIMIT 1;")
        res3 = await db.execute(q3)
        sample = res3.fetchone()
        if sample:
            print(f"Sample Data: ID={sample[0]} (Type: {type(sample[0])}), Name={sample[1]}")
        else:
            print("Sample Data: NO DATA FOUND in stratums table.")

        print("\n[FACT] --- TIMEZONE AUDIT ---")
        q4 = text("SHOW TIMEZONE;")
        res4 = await db.execute(q4)
        print(f"PostgreSQL Timezone: {res4.scalar()}")

if __name__ == "__main__":
    asyncio.run(get_hard_facts())
