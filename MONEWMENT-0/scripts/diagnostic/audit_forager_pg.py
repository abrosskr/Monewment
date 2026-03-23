import asyncio
import os
import sys
from pathlib import Path

# MONEWMENT-0 폴더를 path에 추가
root = Path(r"c:\monewment")
sys.path.insert(0, str(root / "MONEWMENT-0"))

# .env 로드
env_path = root / "MONEWMENT-0" / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

try:
    from core.database import engine
    from sqlalchemy import text
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

async def audit_all_schemas():
    async with engine.connect() as conn:
        print("--- [AUDIT] Checking ALL Schemas in PostgreSQL ---")
        
        schemas_res = await conn.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')"))
        all_schemas = [row[0] for row in schemas_res.fetchall()]
        
        for schema in all_schemas:
            try:
                tables_res = await conn.execute(text(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}'"))
                tables = [row[0] for row in tables_res.fetchall()]
                if not tables:
                    continue
                
                print(f"\n[Schema: {schema}]")
                for table in tables:
                    try:
                        count_res = await conn.execute(text(f"SELECT count(*) FROM {schema}.{table}"))
                        count = count_res.scalar()
                        if count > 100:
                            print(f"  - {table}: {count:,} rows")
                    except Exception as e:
                        pass
            except Exception as e:
                print(f"[!] Error checking schema {schema}: {e}")

if __name__ == "__main__":
    asyncio.run(audit_all_schemas())
