import asyncio
import os
import sys
import time
from datetime import datetime
from sqlalchemy import text
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

from core.database import AsyncSessionLocal
from core.logger import logger

# ==============================================================================
# 👸 QUEEN SENTRY DASHBOARD v1.0
# ==============================================================================

async def get_queen_status():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("""
            SELECT 
                queen_name, 
                queen_type, 
                status, 
                active_ant_count, 
                total_tasks_completed, 
                last_seen_at,
                born_at
            FROM schema_registry.queens
            ORDER BY last_seen_at DESC
        """))
        return result.fetchall()

def format_time_diff(dt):
    if not dt: return "NEVER"
    diff = datetime.now(dt.tzinfo) - dt
    seconds = diff.total_seconds()
    if seconds < 60: return f"{int(seconds)}s ago"
    return dt.strftime("%H:%M:%S")

async def run_dashboard():
    try:
        while True:
            queens = await get_queen_status()
            
            # Clear screen
            os.system('cls' if os.name == 'nt' else 'clear')
            
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"  [QUEEN SENTRY] Unified Hive Command | {now}")
            print("=" * 90)
            print(f"  {'QUEEN NAME':<25} | {'TYPE':<12} | {'STATUS':<10} | {'ANTS':>5} | {'TASKS':>8} | {'LAST SEEN'}")
            print("-" * 90)
            
            active_count = 0
            for q in queens:
                name, q_type, status, ants, tasks, last_seen, born = q
                
                # ASCII Status Indicator
                icon = "[+]" if status == "ACTIVE" else "[ ]"
                if status == "DEAD": icon = "[X]"
                
                # Activity indicator
                is_working = "Y" if ants > 0 else "N"
                
                last_seen_str = format_time_diff(last_seen)
                
                print(f" {icon} {name[:22]:<22} | {q_type:<12} | {status:<10} | {ants:>5} | {tasks:>8} | {last_seen_str}")
                
                if status == "ACTIVE":
                    active_count += 1
            
            print("-" * 90)
            print(f"  [SUMMARY] Total Queens: {len(queens)} | Active: {active_count} | Hive Health: {'STABLE' if active_count > 0 else 'CRITICAL'}")
            print(f"  [CMD] Ctrl+C to exit | Refresh: 3s")
            
            await asyncio.sleep(3)
    except KeyboardInterrupt:
        print("\n[!] Dashboard terminated.")
    except Exception as e:
        print(f"\n[ERROR] Dashboard failure: {e}")

if __name__ == "__main__":
    asyncio.run(run_dashboard())
