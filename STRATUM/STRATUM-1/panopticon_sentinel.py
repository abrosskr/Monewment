import asyncio
import socket
import httpx
import os
import sys
import psutil
import subprocess
import logging
import time
from datetime import datetime
from typing import Optional

# [V51.5] PATH RESOLUTION
# STRATUM-1 is the primary dispatcher. Core modules are sourced from MONEWMENT-0.
STRATUM1_PATH = os.path.abspath(os.path.dirname(__file__))
CORE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "MONEWMENT-0"))
if CORE_PATH not in sys.path:
    sys.path.append(CORE_PATH)

try:
    from core.constants import GATEWAY_PORT
    from core.config import settings
except ImportError:
    # Fallback if pathing fails during boot
    GATEWAY_PORT = 8800
    class MockSettings:
        GATEWAY_TOKEN = "mon_gw_ch4ng3m3_bef0re_pr0d"
    settings = MockSettings()

# --- CONFIGURATION ---
CHECK_INTERVAL = 30  # Seconds
RECOVERY_COOLDOWN = 60  # Seconds
MAX_RETRIES = 3
HEALTH_ENDPOINT = f"http://127.0.0.1:{GATEWAY_PORT}/health"
LOG_FILE = "logs/IMPERIAL_RECOVERY.log"

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] SENTINEL: %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)
logger = logging.getLogger("Sentinel")

class PanopticonSentinel:
    """
    Autonomous Self-Healing Sentinel for MONEWMENT Core Dispatcher (STRATUM-1).
    Monitors Port 8800 and restores order upon entropy detection.
    """
    def __init__(self):
        self.consecutive_failures = 0
        self.last_recovery_time = 0.0
        self.is_quarantined = False

    async def check_l4_socket(self) -> bool:
        """Layer 4: TCP Socket Connectivity Check."""
        try:
            with socket.create_connection(("127.0.0.1", GATEWAY_PORT), timeout=2):
                return True
        except (socket.timeout, ConnectionRefusedError):
            return False

    async def check_l7_http(self) -> bool:
        """Layer 7: HTTP Application Health Check."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(HEALTH_ENDPOINT)
                return response.status_code == 200
        except Exception:
            return False

    def get_zombie_pids(self):
        """Identifies processes squatting on the target port."""
        zombies = []
        for conn in psutil.net_connections():
            if conn.laddr.port == GATEWAY_PORT and conn.status == 'LISTEN':
                if conn.pid:
                    zombies.append(conn.pid)
        return list(set(zombies))

    async def purge_and_ignite(self):
        """Executes the Great Cleansing and Restoration sequence."""
        logger.warning("Initiating Restoration Sequence (Zero-Entropy Protocol)...")
        
        # 1. Purge Zombies
        pids = self.get_zombie_pids()
        for pid in pids:
            try:
                proc = psutil.Process(pid)
                logger.info(f"Terminating Zombie Process PID: {pid} ({proc.name()})")
                proc.kill()
            except Exception as e:
                logger.error(f"Failed to kill PID {pid}: {e}")

        # 2. Cleanup Sockets/Temp
        # Cleanup temp files from STRATUM-1 working directory
        temp_path = os.path.join(STRATUM1_PATH, ".temp")
        if os.path.exists(temp_path):
            for f in os.listdir(temp_path):
                try:
                    os.remove(os.path.join(temp_path, f))
                except: pass

        # 3. Ignite Core
        try:
            logger.info("Igniting Core via start.py...")
            # Use the same python interpreter
            subprocess.Popen(
                [sys.executable, "start.py"],
                cwd=os.getcwd(),
                start_new_session=True
            )
            logger.info("Ignition signal sent. Awaiting stabilization.")
            await asyncio.sleep(10) # Stabilization grace period
        except Exception as e:
            logger.error(f"Ignition failed: {e}")

    async def run(self):
        logger.info(f"Panopticon Sentinel Active. Monitoring Port {GATEWAY_PORT}...")
        
        while True:
            if self.is_quarantined:
                logger.critical("SYSTEM IN QUARANTINE. Manual intervention required.")
                await asyncio.sleep(300)
                continue

            l4_ok = await self.check_l4_socket()
            l7_ok = await self.check_l7_http() if l4_ok else False

            if l4_ok and l7_ok:
                if self.consecutive_failures > 0:
                    logger.info("Order Restored. Resetting failure counters.")
                self.consecutive_failures = 0
            else:
                self.consecutive_failures += 1
                logger.error(f"Entropy Detected! (Failure {self.consecutive_failures}/{MAX_RETRIES})")
                
                if self.consecutive_failures >= MAX_RETRIES:
                    if time.time() - self.last_recovery_time > RECOVERY_COOLDOWN:
                        await self.purge_and_ignite()
                        self.last_recovery_time = time.time()
                    else:
                        logger.warning("Recovery on cooldown. Backing off.")
                    
                    if self.consecutive_failures >= MAX_RETRIES * 2:
                        logger.critical("MAX RETRIES EXCEEDED. Transitioning to QUARANTINE mode.")
                        self.is_quarantined = True

            await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    sentinel = PanopticonSentinel()
    try:
        asyncio.run(sentinel.run())
    except KeyboardInterrupt:
        logger.info("Sentinel standing down.")
