import asyncio
import psutil
from datetime import datetime
import os
import sqlite3
import logging
from core.config import settings

class PhysicsMonitor:
    def __init__(self, governor):
        self.governor = governor
        self.logger = governor.logger

    async def run(self):
        while True:
            try:
                # Audit
                cpu = psutil.cpu_percent()
                mem = psutil.virtual_memory().percent
                if cpu > 80 or mem > 90:
                    self.logger.warning(f"HIGH RESOURCE USAGE: CPU {cpu}%, MEM {mem}%")
                
                # Zombie Hunt
                self.hunt_zombies()
                
                # Heartbeat to local registry
                self.governor.update_local_registry(self.governor.sovereign_id, "QUEEN", "MONITORING_ACTIVE")
                
                await asyncio.sleep(5)
            except Exception as e:
                self.logger.error(f"Monitor error: {e}")
                await asyncio.sleep(5)

    def hunt_zombies(self):
        try:
            for proc in psutil.process_iter(['pid', 'ppid', 'status']):
                if proc.info['ppid'] == 1 and proc.info['status'] == psutil.STATUS_ZOMBIE:
                    self.logger.critical(f"ZOMBIE DETECTED: {proc.info['pid']}. Purging...")
                    # proc.kill()
        except Exception:
            pass
