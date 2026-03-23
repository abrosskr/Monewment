import asyncio
import os
import sys
from datetime import datetime
from sqlalchemy import text
from pathlib import Path
from typing import Dict, Any

# MONEWMENT-0 Core path imports
sys.path.append(str(Path(__file__).parent))
from core.database import create_async_engine, async_sessionmaker
from core.config import settings

# ==============================================================================
# 🏟️ SOVEREIGN DASHBOARD v3.2 — Elite Oversight
# ==============================================================================

# MONEWMENT-0 Core path imports
sys.path.append(str(Path(__file__).parent))
from core.database import engine, AsyncSessionLocal
from core.config import settings

IMPERIAL_CLASSES = ["GUARD", "CHRONOS", "CCTV", "MAP", "ORCHESTRA"]

async def get_imperial_stats():
    async with AsyncSessionLocal() as session:
        # 1. Hierarchical Summary (Living entities only, seen in last 5 mins)
        mon_count = (await session.execute(text("SELECT count(*) FROM schema_registry.monewments WHERE status != 'DEAD' AND last_seen_at > NOW() - INTERVAL '5 minutes'"))).scalar() or 0
        str_count = (await session.execute(text("SELECT count(*) FROM schema_registry.stratums WHERE status != 'DEAD' AND last_seen_at > NOW() - INTERVAL '5 minutes'"))).scalar() or 0
        que_count = (await session.execute(text("SELECT count(*) FROM schema_registry.queens WHERE status != 'DEAD' AND last_seen_at > NOW() - INTERVAL '5 minutes'"))).scalar() or 0
        ant_count = (await session.execute(text("SELECT count(*) FROM schema_registry.ants WHERE status != 'DEAD' AND last_seen_at > NOW() - INTERVAL '5 minutes'"))).scalar() or 0

        # 2. Detailed Population & Status Cross-Section
        # Result set mapping: row[0]=ant_type, row[1]=status, row[2]=cnt
        rows = (await session.execute(text("""
            SELECT ant_type, status, count(*) as cnt 
            FROM schema_registry.ants 
            WHERE status != 'DEAD' AND last_seen_at > NOW() - INTERVAL '5 minutes'
            GROUP BY ant_type, status
        """))).all()
        
        # Structure data: {ant_type: {"WORKING": int, "IDLE": int, "TOTAL": int}}
        pop_data: Dict[str, Dict[str, int]] = {}
        for row in rows:
            r_type = str(row[0] or "UNKNOWN")
            r_status = str(row[1] or "DORMANT")
            r_cnt = int(row[2] or 0)
            
            if r_type not in pop_data:
                pop_data[r_type] = {"WORKING": 0, "IDLE": 0, "TOTAL": 0}
            
            if r_status in ("ACTIVE", "RUNNING"):
                pop_data[r_type]["WORKING"] += r_cnt
            else:
                pop_data[r_type]["IDLE"] += r_cnt
            pop_data[r_type]["TOTAL"] += r_cnt

        return {
            "hierarchy": {"MON": mon_count, "STR": str_count, "QUE": que_count, "ANT": ant_count},
            "population": pop_data,
            "total_ants": int(ant_count)
        }

def get_ratio_status(ratio: float) -> str:
    if 10 <= ratio <= 15: return "OPTIMAL"
    if ratio < 10: return "LEAN (UNDER)"
    return "HEAVY (OVER)"

async def run_dashboard():
    try:
        while True:
            stats = await get_imperial_stats()
            # Safety check if stats is None or unexpected
            if not stats:
                await asyncio.sleep(5)
                continue
                
            os.system('cls' if os.name == 'nt' else 'clear')
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            hierarchy = stats.get("hierarchy", {})
            pop = stats.get("population", {})
            total_ants = int(stats.get("total_ants", 1))
            if total_ants == 0: total_ants = 1
            
            # Type safe aggregation for Imperial Ratio
            imperial_total = 0
            for cls in IMPERIAL_CLASSES:
                cls_data = pop.get(cls, {"WORKING": 0, "IDLE": 0, "TOTAL": 0})
                imperial_total += int(cls_data.get("TOTAL", 0))
                    
            imperial_ratio = (imperial_total / total_ants) * 100
            
            W = 100
            print(f"  [DASHBOARD] SOVEREIGN DASHBOARD v3.2 | {now}")
            print("=" * W)
            
            # --- Hierarchy Overview ---
            print(f"  [EMPIRE] MON: {hierarchy.get('MON', 0)} | STR: {hierarchy.get('STR', 0)} | QUE: {hierarchy.get('QUE', 0)} | TOTAL_ANT: {total_ants}")
            print("-" * W)

            # --- Regime Stability (Ratios) ---
            r_status = get_ratio_status(imperial_ratio)
            print(f"  [REGIME] Imperial Ratio: {imperial_ratio:>5.1f}% | Status: [{r_status}] | Target: 10-15%")
            print("-" * W)

            # --- Detailed Population Breakdown ---
            print(f"  {'[CLASS]':<20} | {'WORKING':>10} | {'IDLE':>10} | {'TOTAL':>10} | {'RATIO':>10}")
            print("-" * W)
            
            # 1. Imperial Classes first
            print("  -- IMPERIAL CIVIL SERVICE --")
            for cls in IMPERIAL_CLASSES:
                d = pop.get(cls, {"WORKING": 0, "IDLE": 0, "TOTAL": 0})
                ratio = (int(d.get("TOTAL", 0)) / total_ants) * 100
                print(f"  {cls:<20} | {int(d.get('WORKING', 0)):>10,} | {int(d.get('IDLE', 0)):>10,} | {int(d.get('TOTAL', 0)):>10,} | {ratio:>9.1f}%")
            
            print("-" * W)
            # 2. Other Classes (Serfs)
            print("  -- SUBJECT POPULATION (SERFS) --")
            for cls, d in pop.items():
                if cls in IMPERIAL_CLASSES: continue
                ratio = (int(d.get("TOTAL", 0)) / total_ants) * 100
                print(f"  {cls:<20} | {int(d.get('WORKING', 0)):>10,} | {int(d.get('IDLE', 0)):>10,} | {int(d.get('TOTAL', 0)):>10,} | {ratio:>9.1f}%")

            print("=" * W)
            print(f"  [INTEGRITY] Sovereign Health: {'EXCELLENT' if r_status == 'OPTIMAL' else 'VIGILANT'}")
            print(f"  [CMD] Ctrl+C to disconnect | Refresh: 5s")

            await asyncio.sleep(5)
    except KeyboardInterrupt:
        print("\n[!] Dashboard disconnected.")
    finally:
        # We don't dispose the global engine to avoid side effects on other components
        pass

if __name__ == "__main__":
    asyncio.run(run_dashboard())
