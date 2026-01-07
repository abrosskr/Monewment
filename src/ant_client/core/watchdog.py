import subprocess
import sys
import time
import logging
import os
from pathlib import Path

# Setup simple logger for Watchdog
logging.basicConfig(level=logging.INFO, format='%(asctime)s [WATCHDOG] %(message)s')
logger = logging.getLogger("Watchdog")

class Watchdog:
    def __init__(self, target_script: str):
        self.target_script = target_script
        self.process = None
        
    def start_worker(self):
        """Starts the worker process."""
        cmd = [sys.executable, self.target_script]
        logger.info(f"Starting worker: {' '.join(cmd)}")
        
        # Pass current environment variable
        env = os.environ.copy()
        
        self.process = subprocess.Popen(cmd, env=env)
        
    def monitor(self):
        """Monitors the worker process and restarts if it dies."""
        self.start_worker()
        
        while True:
            try:
                # Check if process is still running
                retcode = self.process.poll()
                
                if retcode is not None:
                    logger.warning(f"Worker process exited with code {retcode}. Restarting in 3 seconds...")
                    time.sleep(3)
                    self.start_worker()
                else:
                    # Process is healthy
                    time.sleep(5)
                    
            except KeyboardInterrupt:
                logger.info("Watchdog stopped by user.")
                self.stop()
                break
            except Exception as e:
                logger.error(f"Watchdog error: {e}")
                time.sleep(5)

    def stop(self):
        if self.process:
            logger.info("Terminating worker process...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()

if __name__ == "__main__":
    # Assuming this runs from project root or src/ant_client
    # Target: src/ant_client/worker_main.py (We will create this next)
    current_dir = Path(__file__).parent.parent
    worker_script = current_dir / "worker_main.py"
    
    dog = Watchdog(str(worker_script))
    dog.monitor()
