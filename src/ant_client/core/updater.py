import requests
import logging
import sys
import os
import subprocess

logger = logging.getLogger("Updater")

class Updater:
    def __init__(self, server_url: str, current_version: str):
        self.server_url = server_url
        self.current_version = current_version
        
    def check_and_update(self) -> bool:
        """
        Checks for updates. If available, performs update and returns True.
        Returns False if no update needed.
        """
        try:
            logger.info(f"Checking for updates... (Current: {self.current_version})")
            resp = requests.get(f"{self.server_url}/api/client/version", timeout=5)
            
            if resp.status_code != 200:
                logger.warning("Failed to check version.")
                return False
                
            data = resp.json()
            server_version = data.get("version")
            download_url = data.get("download_url") # Not used in Git pull mode
            
            if server_version != self.current_version:
                logger.info(f"🚀 New version available: {server_version}")
                return self._perform_update()
                
            logger.info("✅ Client is up to date.")
            return False
            
        except Exception as e:
            logger.error(f"Update check failed: {e}")
            return False

    def _perform_update(self) -> bool:
        """
        Performs the update mechanism.
        For this source-based deployment, we assume `git pull`.
        In a binary distribution, this would download the exe and swap it.
        """
        try:
            logger.info("📦 Pulling latest code from repository...")
            # Git Pull
            # Assuming current dir is the repo root or inside it
            res = subprocess.run(["git", "pull"], capture_output=True, text=True)
            
            if res.returncode == 0:
                logger.info(f"Update Success: {res.stdout}")
                logger.info("🔄 Restarting client...")
                # Restart the current process
                os.execv(sys.executable, [sys.executable] + sys.argv)
                return True # Actually never reached due to execv
            else:
                logger.error(f"Git Pull Failed: {res.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Update failed: {e}")
            return False
