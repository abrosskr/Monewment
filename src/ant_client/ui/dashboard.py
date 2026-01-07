import subprocess
import logging
import os
import sys
import shutil
import json

logger = logging.getLogger("AntDashboard")

class AntDashboard:
    def __init__(self, on_auth_success=None):
        self.process = None
        self.on_auth_success = on_auth_success

    def _find_edge(self):
        """Locate Microsoft Edge executable on Windows"""
        paths = [
            os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)") + "\\Microsoft\\Edge\\Application\\msedge.exe",
            os.environ.get("ProgramFiles", "C:\\Program Files") + "\\Microsoft\\Edge\\Application\\msedge.exe",
            shutil.which("msedge")
        ]
        for p in paths:
            if p and os.path.exists(p):
                return p
        return None

    def start(self, url="http://localhost:3000/login?context=client", hidden=False):
        if hidden:
            logger.info("Dashboard silent start requested (Worker only).")
            return

        edge_path = self._find_edge()
        if not edge_path:
            logger.error("❌ Microsoft Edge not found. Please install Edge for the native experience.")
            # Fallback to default browser if absolutely necessary
            import webbrowser
            webbrowser.open(url)
            return

        logger.info(f"🚀 Launching Enterprise Edge Link: {url}")
        
        # Edge App Mode flags
        # --app: Launches ohne Address Bar/Tabs
        # --window-size: 초기 크기
        # --user-data-dir: 독립된 세션 유지 (Optional)
        cmd = [
            edge_path,
            f"--app={url}",
            "--window-size=1280,800",
            "--start-maximized",
            "--window-name=MonewmentAntDashboard"
        ]
        
        try:
            self.process = subprocess.Popen(cmd)
        except Exception as e:
            logger.error(f"Failed to launch Edge App: {e}")

    def show(self):
        # Edge App mode doesn't support easy 'show/hide' via Popen 
        # unless we use complex Win32 APIs. 
        # For simplicity, we just relaunch if the process is gone, 
        # or use a default URL.
        if not self.process or self.process.poll() is not None:
             self.start()

    def hide(self):
        # We can't easily hide the Edge window from here without Win32 hooks.
        # But we can terminate it if the user wants it 'hidden' (and they can reopen via Tray)
        if self.process:
            self.process.terminate()

    def load_config(self):
        """Load persistent config from disk"""
        config_path = os.path.expanduser("~/.monewment/client_config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        return {}

    def save_config(self, config):
        """Save config to disk"""
        config_path = os.path.expanduser("~/.monewment/client_config.json")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        try:
            with open(config_path, "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def navigate(self, url):
        # Navigation in Edge App mode is handled by relaunching with the new URL
        self.start(url)

    def resize(self, width, height):
        # No-op for Edge App Mode as resizing via Popen is complex
        logger.info(f"Resize requested to {width}x{height} (Ignored in Edge App Mode)")
        pass
