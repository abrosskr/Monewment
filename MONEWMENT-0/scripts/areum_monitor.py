import asyncio
import os
import sys
import time
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.console import Console
from rich import box

# --- [V51.5.1 PATH INJECTION] ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from core.config import settings
except ImportError:
    print("[CRITICAL] Could not import core.config. Run from MONEWMENT-0 root or scripts folder.")
    sys.exit(1)

console = Console()

# Database Setup
engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0,
    }
)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def fetch_stats():
    async with AsyncSessionLocal() as db:
        try:
            # 1. AREUM Registry Status
            res_reg = await db.execute(text("""
                SELECT areum_id, areum_name, status, reports_sent, last_seen_at 
                FROM schema_pipeline.areum_registry 
                ORDER BY reports_sent DESC
            """))
            registry = res_reg.fetchall()

            # 2. Learning Queue Status
            res_queue = await db.execute(text("""
                SELECT status, COUNT(*) 
                FROM schema_rex.learning_queue 
                GROUP BY status
            """))
            queue_stats = res_queue.fetchall()

            # 3. Recent reports from "AREUM-1" (or top areum)
            res_recent = await db.execute(text("""
                SELECT report_id, report_type, received_at, processing_status
                FROM schema_rex.areum_reports
                ORDER BY received_at DESC
                LIMIT 10
            """))
            recent_reports = res_recent.fetchall()

            return {
                "registry": registry,
                "queue": dict(queue_stats),
                "recent": recent_reports
            }
        except Exception as e:
            return {"error": str(e)}

def generate_dashboard(data):
    if "error" in data:
        return Panel(f"[red]Error fetching data: {data['error']}[/red]", title="MONEWMENT Core Error")

    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3)
    )
    
    # Header
    layout["header"].update(Panel(f"[bold gold1]🏛️ MONEWMENT AREUM-1 INTELLIGENCE DASHBOARD[/bold gold1] | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", box=box.DOUBLE))

    # Main area split
    layout["main"].split_row(
        Layout(name="left"),
        Layout(name="right")
    )

    # Left: AREUM Registry
    reg_table = Table(title="📡 AREUM Registry", box=box.ROUNDED)
    reg_table.add_column("Name", style="cyan")
    reg_table.add_column("Status", style="green")
    reg_table.add_column("Reports", style="magenta", justify="right")
    reg_table.add_column("Last Seen", style="dim")

    for row in data["registry"]:
        status_style = "green" if row[2] == "ACTIVE" else "red"
        reg_table.add_row(
            row[1], 
            f"[{status_style}]{row[2]}[/{status_style}]", 
            str(row[3]), 
            row[4].strftime("%H:%M:%S") if row[4] else "N/A"
        )
    layout["left"].update(reg_table)

    # Right: Learning Queue & Recent Reports
    right_col = Layout()
    right_col.split_column(
        Layout(name="queue_panel", size=7),
        Layout(name="recent_panel")
    )

    # Queue Panel
    q = data["queue"]
    q_table = Table(title="🧠 REX Learning Queue", box=box.MINIMAL)
    q_table.add_column("Status", style="bold")
    q_table.add_column("Count", justify="right")
    
    for s in ["QUEUED", "IN_PROGRESS", "ASSIMILATED", "FAILED"]:
        count = q.get(s, 0)
        style = "yellow" if s == "QUEUED" else "blue" if s == "IN_PROGRESS" else "green" if s == "ASSIMILATED" else "red"
        q_table.add_row(f"[{style}]{s}[/{style}]", str(count))
    
    right_col["queue_panel"].update(Panel(q_table, border_style="blue"))

    # Recent Reports Panel
    rec_table = Table(title="📄 Recent Intelligence Reports", box=box.SIMPLE)
    rec_table.add_column("ID", style="dim", width=8)
    rec_table.add_column("Type", style="cyan")
    rec_table.add_column("Time", style="dim")
    rec_table.add_column("State", style="bold")

    for r in data["recent"]:
        state_style = "green" if r[3] == "PROCESSED" else "yellow"
        rec_table.add_row(str(r[0])[:8], r[1], r[2].strftime("%H:%M:%S"), f"[{state_style}]{r[3]}[/{state_style}]")
    
    right_col["recent_panel"].update(rec_table)
    layout["right"].update(right_col)

    # Footer
    layout["footer"].update(Panel("[dim]Press Ctrl+C to terminate the Imperial Monitor.[/dim]", box=box.SIMPLE))

    return layout

async def main():
    with Live(console=console, refresh_per_second=1, screen=True) as live:
        while True:
            data = await fetch_stats()
            live.update(generate_dashboard(data))
            await asyncio.sleep(2)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
