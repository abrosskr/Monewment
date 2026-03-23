import asyncio
import os
import sys
from pathlib import Path
from sqlalchemy import text

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

from core.database import engine

async def check():
    async with engine.connect() as conn:
        print("--- [TARGET SITE AUDIT] ---")
        try:
            res = await conn.execute(text("SELECT domain, display_name, is_active FROM schema_stratum_vendors.target_site"))
            rows = res.fetchall()
            for r in rows:
                print(f"Domain: {r[0]} | Name: {r[1]} | Active: {r[2]}")
        except Exception as e:
            print(f"Error checking vendors.target_site: {e}")

        print("\n--- [FORAGER CRAWL SCHEMA AUDIT] ---")
        try:
            tables_res = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'schema_stratum_forager_crawl'"))
            tables = [row[0] for row in tables_res.fetchall()]
            print(f"Tables in schema_stratum_forager_crawl: {tables}")
            for t in tables:
                count_res = await conn.execute(text(f"SELECT count(*) FROM schema_stratum_forager_crawl.{t}"))
                print(f" - {t}: {count_res.scalar():,} rows")
        except Exception as e:
            print(f"Error checking forager_crawl schema: {e}")

if __name__ == "__main__":
    asyncio.run(check())
