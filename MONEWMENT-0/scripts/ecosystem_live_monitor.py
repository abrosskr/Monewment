import asyncio
import time
from sqlalchemy import text
from core.database import engine

async def live_monitor():
    print("=== Imperial Ecosystem Live Monitor (V49) ===")
    print("Tracing data flow from Forager to REX...")
    
    last_count = 0
    while True:
        async with engine.connect() as conn:
            # 1. Assets count
            res_a = await conn.execute(text("SELECT COUNT(*) FROM schema_stratum_vendors.assets"))
            asset_count = res_a.scalar()
            
            # 2. Latest reports
            res_r = await conn.execute(text("""
                SELECT areum_id, report_type, processing_status, received_at 
                FROM schema_rex.areum_reports 
                ORDER BY received_at DESC LIMIT 3
            """))
            reports = res_r.fetchall()
            
            # 3. Active Ants
            res_ant = await conn.execute(text("SELECT COUNT(*) FROM schema_registry.ants WHERE status = 'ACTIVE'"))
            ant_count = res_ant.scalar()

            print(f"\n[{time.strftime('%H:%M:%S')}] Assets: {asset_count} | Active Ants: {ant_count}")
            if reports:
                for r in reports:
                    print(f"  REPORT: {r.report_type} from {r.areum_id} ({r.processing_status})")
            else:
                print("  No reports yet.")
                
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(live_monitor())
