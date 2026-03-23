import os
import sys
import subprocess
import time
import signal
import logging
import argparse
from typing import Dict, List, Optional

# Add project root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.config import settings
from core.logger import logger

class ImperialSpawnEngine:
    """
    MONEWMENT Imperial Spawn Engine v3.2 (Sovereign Edition)
    Handles the lifecycle of Civil Servant ANTs with Registry Integration.
    """
    
    def __init__(self):
        self.active_servants: Dict[str, subprocess.Popen] = {}
        self.task_counters: Dict[str, int] = {}
        self.max_tasks_per_process = 10 
        
    def spawn_servant(self, ant_class: str, ant_id: str):
        """Spawns an Imperial ANT with standardized logging and registration."""
        logger.info(f"[IMPERIAL] Recruitment started: {ant_id} ({ant_class})")
        
        log_dir = os.path.join("logs", "imperial")
        os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(log_dir, f"{ant_id}.log")
        log_file = open(log_file_path, "a")
        
        # Determine script
        script = "core/imperial_worker_proxy.py"
        if ant_class == "GUARD":
            script = "imperial_guard_ant.py"
            
        cmd = [
            sys.executable, 
            script, 
            "--class", ant_class,
            "--id", ant_id
        ]
        
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=log_file,
                stderr=log_file,
                start_new_session=True,
                cwd="c:/monewment/MONEWMENT-0"
            )
            self.active_servants[ant_id] = proc
            self.task_counters[ant_id] = 0
            logger.info(f"[IMPERIAL] {ant_id} is now ACTIVE. Monitoring: {log_file_path}")
        except Exception as e:
            logger.error(f"[IMPERIAL] Failed to spawn {ant_id}: {e}")

    def monitor_and_replace(self):
        """Maintain the registry health and perform Eternal Shield replacement."""
        for ant_id, proc in list(self.active_servants.items()):
            if proc.poll() is not None:
                logger.warning(f"[IMPERIAL] {ant_id} has died. Initiating resurrection...")
                ant_class = ant_id.split("-")[0]
                self.spawn_servant(ant_class, ant_id)
                continue

    def stop_all(self):
        for ant_id, proc in self.active_servants.items():
            proc.terminate()
        logger.info("[IMPERIAL] All servants dismissed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    
    engine = ImperialSpawnEngine()
    
    # Initial Recruitment Quota
    initial_quota = {
        "GUARD": 2,
        "CHRONOS": 1,
        "CCTV": 2,
        "MAP": 1,
        "ORCHESTRA": 1
    }
    
    for cls, count in initial_quota.items():
        for i in range(count):
            engine.spawn_servant(cls, f"{cls}-SERVICE-{i}")
            
    if args.once:
        logger.info("[IMPERIAL] Initial recruitment cycle complete.")
        sys.exit(0)
        
    try:
        while True:
            engine.monitor_and_replace()
            time.sleep(10)
    except KeyboardInterrupt:
        engine.stop_all()
