import asyncio
import os
import sys
import json
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.console import Console
from rich import box
from rich.progress import BarColumn, Progress, TextColumn

# --- [STRATUM CONFIGURATION] ---
STRATUM_NAME = settings.STRATUM_NAME
STRATUM_ID = settings.STRATUM_ID
SCHEMA_NAME = f"schema_stratum_{STRATUM_NAME}"

# Path Injection
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from core.config import settings
except ImportError:
    # Fallback to absolute paths if relative import fails
    sys.path.append(r"c:\monewment\STRATUM\STRATUM-1")
    from core.config import settings

console = Console()

# Database Setup
engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={"prepared_statement_cache_size": 0, "statement_cache_size": 0}
)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def fetch_stratum_data():
    async with AsyncSessionLocal() as db:
        try:
            # 1. Total Assets vs Extracted Assets
            total_assets_res = await db.execute(text(f"SELECT COUNT(*) FROM {SCHEMA_NAME}.assets"))
            total_assets = total_assets_res.scalar() or 0

            extracted_res = await db.execute(text(f"SELECT COUNT(*) FROM {SCHEMA_NAME}.areum_extraction"))
            extracted_assets = extracted_res.scalar() or 0

            enhanced_res = await db.execute(text(f"SELECT COUNT(*) FROM {SCHEMA_NAME}.premium_enhanced"))
            enhanced_assets = enhanced_res.scalar() or 0

            # 2. Local AREUM Status (Dynamic Harmonization)
            areum_res = await db.execute(text(f"""
                SELECT name, status, last_seen_at FROM (
                    SELECT areum_name as name, status, last_seen_at FROM schema_pipeline.areum_registry WHERE stratum_id = CAST(:sid AS uuid)
                    UNION
                    SELECT ant_name as name, status, last_seen_at FROM schema_registry.ants WHERE stratum_id = CAST(:sid AS uuid) AND ant_type LIKE '%AREUM%'
                ) combined
                ORDER BY last_seen_at DESC
            """), {"sid": STRATUM_ID})
            areums = areum_res.fetchall()

            # 3. Recent Extractions with Sample Intelligence
            recent_res = await db.execute(text(f"""
                SELECT COALESCE(h.url, a.raw_data->>'url', 'N/A') as url, 
                       e.confidence_score, e.extracted_at, e.extracted_data
                FROM {SCHEMA_NAME}.areum_extraction e
                JOIN {SCHEMA_NAME}.assets a ON e.asset_id = a.id
                LEFT JOIN {SCHEMA_NAME}.scout_history h ON a.hash = h.content_hash
                ORDER BY e.extracted_at DESC
                LIMIT 5
            """))
            recent = recent_res.fetchall()

            return {
                "total": total_assets,
                "extracted": extracted_assets,
                "enhanced": enhanced_assets,
                "areums": areums,
                "recent": recent
            }
        except Exception as e:
            return {"error": str(e)}

def generate_dashboard(data):
    if "error" in data:
        return Panel(f"[red]Audit Error: {data['error']}[/red]", title="STRATUM-1 G5 RECOVERY")

    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3)
    )

    # Header
    layout["header"].update(Panel(
        f"[bold cyan]🏰 STRATUM-1 | AREUM Intelligence Monitor (V51.5.1)[/bold cyan] | {datetime.now().strftime('%H:%M:%S')}", 
        box=box.DOUBLE
    ))

    # Main Area
    layout["main"].split_row(
        Layout(name="metrics", ratio=1),
        Layout(name="intelligence", ratio=2)
    )

    # Left: Metrics & Status
    metrics_layout = Layout()
    metrics_layout.split_column(
        Layout(name="progress_box", size=10),
        Layout(name="areum_box")
    )

    # Progress Bar Table
    progress = Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=20),
        TextColumn("[magenta]{task.percentage:>3.0f}%"),
    )
    progress.add_task("Extraction", total=data["total"] or 1, completed=data["extracted"])
    progress.add_task("REX Enhancement", total=data["total"] or 1, completed=data["enhanced"])

    metrics_table = Table.grid(padding=1)
    metrics_table.add_row(f"[white]Total Assets:[/white] [bold]{data['total']}[/bold]")
    metrics_table.add_row(progress)
    
    metrics_layout["progress_box"].update(Panel(metrics_table, title="📊 Extraction Progress", border_style="cyan"))

    # AREUM Status
    areum_table = Table(title="🤖 Active AREUM Units", box=box.SIMPLE_HEAD, expand=True)
    areum_table.add_column("Unit", style="dim")
    areum_table.add_column("Status", justify="center")
    areum_table.add_column("Sent", justify="right")

    for a in data["areums"]:
        color = "green" if a[1] == "ACTIVE" else "red"
        areum_table.add_row(a[0], f"[{color}]{a[1]}[/{color}]", str(a[2]))
    
    metrics_layout["areum_box"].update(Panel(areum_table, border_style="blue"))

    layout["metrics"].update(metrics_layout)

    # Right: Intelligence Stream
    intel_table = Table(title="🧠 Intelligence Extraction Stream (V-Learning)", box=box.ROUNDED, expand=True)
    intel_table.add_column("Source URL", style="blue", overflow="fold")
    intel_table.add_column("Conf.", justify="center")
    intel_table.add_column("Insights", style="green")

    for r in data["recent"]:
        # Extract small snippets from JSON data
        intel_json = r[3]
        insights = ""
        if isinstance(intel_json, dict):
            # Try to find interesting fields
            keys = ["title", "summary", "keywords", "ingredients"]
            for k in keys:
                if k in intel_json:
                    val = intel_json[k]
                    if isinstance(val, list): val = ", ".join(map(str, val[:3]))
                    insights = str(val)[:40] + "..."
                    break
        
        intel_table.add_row(r[0][:40] + "...", f"{r[1]*100:.0f}%", insights)

    layout["intelligence"].update(Panel(intel_table, border_style="gold1"))

    # Footer
    layout["footer"].update(Panel(f"[dim]Stratum Node: {STRATUM_ID} | Database: {settings.SUPABASE_HOST}[/dim]", box=box.SIMPLE))

    return layout

async def main():
    with Live(console=console, refresh_per_second=1, screen=True) as live:
        while True:
            data = await fetch_stratum_data()
            live.update(generate_dashboard(data))
            await asyncio.sleep(2)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
