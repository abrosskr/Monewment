import asyncio
import json
from sqlalchemy import text
from core.database import engine

async def full_audit():
    print("=== Imperial Ecosystem Audit (V49) ===")
    async with engine.connect() as conn:
        # 1. Queen Status
        print("\n[QUEENS]")
        res = await conn.execute(text("SELECT queen_id, queen_name, relationship_type, status FROM schema_registry.queens"))
        for r in res.fetchall():
            print(f"  {r.queen_name} ({r.relationship_type}) - STATUS: {r.status} [{r.queen_id}]")

        # 2. Stratum Status
        print("\n[STRATUMS]")
        res = await conn.execute(text("SELECT stratum_id, stratum_name, status FROM schema_registry.stratums"))
        for r in res.fetchall():
            print(f"  {r.stratum_name} - STATUS: {r.status} [{r.stratum_id}]")

        # 3. Active Ants
        print("\n[ACTIVE ANTS]")
        res = await conn.execute(text("SELECT ant_id, ant_name, queen_id, status FROM schema_registry.ants WHERE status = 'ACTIVE'"))
        rows = res.fetchall()
        if not rows:
            print("  No active ants found.")
        for r in rows:
            print(f"  {r.ant_name} (Queen: {r.queen_id}) - STATUS: {r.status} [{r.ant_id}]")

        # 4. Pipeline Reports
        print("\n[PIPELINE REPORTS - LAST 5]")
        res = await conn.execute(text("SELECT report_id, areum_id, report_type, processing_status, received_at FROM schema_rex.areum_reports ORDER BY received_at DESC LIMIT 5"))
        for r in res.fetchall():
            print(f"  {r.received_at} | {r.report_type} from {r.areum_id} - STATUS: {r.processing_status}")

if __name__ == "__main__":
    asyncio.run(full_audit())
