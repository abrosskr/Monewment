import asyncio
import sys
import os
from sqlalchemy import text
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

from core.database import AsyncSessionLocal

async def analyze_rex_intelligence():
    print("=== [REX INTELLIGENCE AUDIT] ===")
    async with AsyncSessionLocal() as session:
        # 1. 원천 데이터(Reports) 상태 분석
        res_reports = await session.execute(text("""
            SELECT processing_status, count(*) 
            FROM schema_rex.areum_reports 
            GROUP BY processing_status
        """))
        reports_summary = res_reports.fetchall()
        print("\n[1] Intelligence Reports Status:")
        for status, count in reports_summary:
            print(f"  - {status:<12}: {count:>4} units")

        # 2. 학습 큐(Learning Queue) 분석
        res_queue = await session.execute(text("""
            SELECT status, count(*) 
            FROM schema_rex.learning_queue 
            GROUP BY status
        """))
        queue_summary = res_queue.fetchall()
        print("\n[2] Learning Queue Progress:")
        for status, count in queue_summary:
            print(f"  - {status:<12}: {count:>4} units")

        # 3. 데이터 다양성 분석 (Report Types)
        res_types = await session.execute(text("""
            SELECT report_type, count(*) 
            FROM schema_rex.areum_reports 
            GROUP BY report_type
        """))
        types_summary = res_types.fetchall()
        print("\n[3] Knowledge Diversity (Report Types):")
        for r_type, count in types_summary:
            print(f"  - {r_type:<15}: {count:>4} units")

        # 4. 최근 학습 완료된 지능 샘플
        res_samples = await session.execute(text("""
            SELECT r.report_type, q.processed_at, r.report_id
            FROM schema_rex.learning_queue q
            JOIN schema_rex.areum_reports r ON q.report_id = r.report_id
            WHERE q.status = 'COMPLETED'
            ORDER BY q.processed_at DESC
            LIMIT 3
        """))
        samples = res_samples.fetchall()
        print("\n[4] Recent Intelligence Assimilated:")
        if not samples:
            print("  - No completed intelligence cycles yet.")
        for r_type, processed_at, r_id in samples:
            print(f"  - {r_type} | {processed_at} | ID: {r_id[:8]}...")

if __name__ == "__main__":
    asyncio.run(analyze_rex_intelligence())
