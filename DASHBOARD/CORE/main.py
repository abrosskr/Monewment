# 🏛️ [DASHBOARD-QUEEN] Imperial Command Center v1.0
# c:\monewment\DASHBOARD\CORE\main.py

import asyncio
import httpx
import os
from datetime import datetime, timezone
from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.console import Console
from rich import box
from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))

# [PROTOCOL SHIELD]
GATEWAY_TOKEN = "mon_gw_ch4ng3m3_bef0re_pr0d"
CORE_URL = "http://127.0.0.1:8800/v1"
HEADERS = {"X-Queen-Token": GATEWAY_TOKEN}

class DashboardQueen:
    def __init__(self):
        self.metrics = {}
        self.survival = []
        self.error_msg = ""

    async def fetch_data(self):
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                # 1. Metrics Harvester
                res_m = await client.get(f"{CORE_URL}/dashboard/metrics", headers=HEADERS)
                if res_m.status_code == 200:
                    self.metrics = res_m.json()
                    self.error_msg = ""
                
                # 2. Heartbeat Sentinel
                res_s = await client.get(f"{CORE_URL}/dashboard/survival", headers=HEADERS)
                if res_s.status_code == 200:
                    self.survival = res_s.json().get("entities", [])
            
            except httpx.ConnectError:
                self.error_msg = "[EMERGENCY: CORE DOWN]"
            except Exception as e:
                self.error_msg = f"[SYSERR: {str(e)}]"

    def make_layout(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=10)
        )
        layout["main"].split_row(
            Layout(name="survival", ratio=1),
            Layout(name="intelligence", ratio=1)
        )
        return layout

    def render_survival(self):
        table = Table(title="Imperial Survival Radar", box=box.ROUNDED, expand=True, border_style="cyan")
        table.add_column("Entity ID", style="dim")
        table.add_column("Territory", style="bold")
        table.add_column("Last Heartbeat", justify="right")
        table.add_column("Status", justify="center")

        now = datetime.now(KST)
        for ent in self.survival:
            ls_str = ent.get("last_seen")
            status = "[bold green]ALIVE[/]"
            if ls_str:
                try:
                    ls_dt = datetime.fromisoformat(ls_str)
                    # [TEMPORAL CONSTITUTION] TZ 정보가 있든 없든 KST Naive 시각으로 간주하여 출력
                    ls_display = ls_dt.strftime("%H:%M:%S")
                    
                    # diff 계산을 위해 naive KST로 통일
                    now_naive = now.replace(tzinfo=None)
                    ls_naive = ls_dt.replace(tzinfo=None) if not ls_dt.tzinfo else ls_dt.astimezone(KST).replace(tzinfo=None)
                    
                    # 만약 ls_dt가 이미 17:xx 형태라면 (KST Naive 가식 저장), astimezone은 오히려 망가뜨릴 수 있음
                    # 하지만 우리 정책상 DB에는 17:xx가 저장되어 있으므로, 
                    # ls_dt.replace(tzinfo=None)만으로도 17:xx를 얻을 수 있음.
                    ls_final = ls_dt.replace(tzinfo=None)
                    diff = (now_naive - ls_final).total_seconds()
                except:
                    ls_display = "ERR"
            else:
                status = "[red]UNKNOWN[/]"
                ls_display = "NEVER"
            
            name = ent.get("name", "Unknown")
            mode = ent.get("mode")
            if mode:
                name = f"{name} [bold yellow]{mode}[/]"
            
            table.add_row(str(ent.get("id", "none"))[:8], name, ls_display, status)
        
        return Panel(table, title="[G3] Heartbeat Sentinel", border_style="blue")

    def render_intelligence(self):
        k = self.metrics.get("knowledge", {})
        r = self.metrics.get("refining", {})
        
        table = Table(box=box.SIMPLE, expand=True)
        table.add_column("Metric", style="yellow")
        table.add_column("Value", style="bold white")
        
        table.add_row("Total Triples", str(k.get("total", 0)))
        table.add_row("Sealed Triples", f"[green]{k.get('sealed', 0)}[/]")
        table.add_row("Yield Rate", f"[bold magenta]{k.get('yield_rate', 0)}%[/]")
        table.add_section()
        table.add_row("RAW Assets", str(r.get("raw", 0)))
        table.add_row("Enhanced Assets", str(r.get("enhanced", 0)))
        table.add_row("DONE Assets", f"[cyan]{r.get('done', 0)}[/]")
        # [UI-ALignment] Mandatory Row Insertion
        table.add_row("Quality Pass Rate", f"[bold green]{r.get('pass_rate', 0)}%[/]")
        table.add_section()
        table.add_row("Production Velocity", f"[bold green]{self.metrics.get('velocity', 0)}/hr[/]")

        return Panel(table, title="[V9.0] Intelligence Harvest", border_style="magenta")

    def render_footer(self):
        recent = self.metrics.get("recent_learning", [])
        # [MANDATORY TASK 2] Real-time Physics Probe Alignment
        physics_path = r"C:\monewment\PHYSICS\PHYSICS-1\data\physics"
        if os.path.exists(physics_path):
            physics_count = len([f for f in os.listdir(physics_path) if f.endswith('.json')])
        else:
            physics_count = self.metrics.get("physics_count", 0)
        
        table = Table(box=box.MINIMAL, expand=True, show_header=False, border_style="green")
        table.add_column("Directive")
        table.add_column("Timestamp", style="dim")
        
        # [MANDATORY TASK 3] REX Learning Feed Loop Resurrection
        if not recent:
            table.add_row("[dim]Waiting for intelligence artifacts...[/]", "")
        else:
            for item in recent[:5]:
                directive = str(item.get('directive', ''))
                at_time = str(item.get('at', ''))[11:19]
                table.add_row(f"▸ {directive[:60]}...", at_time)
            
        return Panel(
            table, 
            title=f"REX Learning Feed | PHYSICS Law Repository: [bold yellow]{physics_count}[/] Files", 
            subtitle=f"System Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            border_style="green"
        )

    async def run(self):
        console = Console()
        layout = self.make_layout()
        
        with Live(layout, refresh_per_second=1, screen=True):
            while True:
                await self.fetch_data()
                
                # Header with Error Alert
                header_msg = "[bold white]MONEWMENT DASHBOARD-QUEEN v1.0[/]"
                if self.error_msg:
                    header_msg = f"{header_msg} | [bold red blink]{self.error_msg}[/]"
                layout["header"].update(Panel(header_msg, style="bold blue", box=box.DOUBLE))
                
                layout["survival"].update(self.render_survival())
                layout["intelligence"].update(self.render_intelligence())
                layout["footer"].update(self.render_footer())
                
                await asyncio.sleep(5)

if __name__ == "__main__":
    queen = DashboardQueen()
    asyncio.run(queen.run())
