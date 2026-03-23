import asyncio
import sys
import os

# MONEWMENT-0 경로 추가
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

from core.database import engine
from sqlalchemy import text
import uuid

async def insert_dummy():
    print("=== [TEST DATA] Inserting dummy PENDING report ===")
    async with engine.begin() as conn:
        report_id = str(uuid.uuid4())
        await conn.execute(text("""
            INSERT INTO schema_rex.areum_reports (report_id, areum_id, report_type, raw_payload, processing_status)
            VALUES (:r_id, 'TEST-AREUM', 'TEST_TYPE', '{"test": true}', 'PENDING')
        """), {"r_id": report_id})
    print(f"[SUCCESS] Inserted dummy report: {report_id}")

if __name__ == "__main__":
    asyncio.run(insert_dummy())
