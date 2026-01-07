import asyncio
import threading
import logging
import sys
import os

import json
import time

# Adjust path for embedded execution
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    BASE_DIR = os.path.dirname(sys.executable)
    sys.path.append(BASE_DIR)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(BASE_DIR)

# Import internal modules
# Note: PyInstaller needs hidden imports for these if dynamic

# [Packaging Fix] Inject Dummy Env Vars for shared Settings validation
# The Client does not need Postgres or Gemini, but shared config.py requires them.
os.environ.setdefault("SECRET_KEY", "client_dummy_key")
os.environ.setdefault("POSTGRES_SERVER", "localhost")
os.environ.setdefault("POSTGRES_USER", "dummy")
os.environ.setdefault("POSTGRES_PASSWORD", "dummy")
os.environ.setdefault("POSTGRES_DB", "dummy")
os.environ.setdefault("GEMINI_API_KEY", "dummy_key")

from src.core.ant_security import AntSecurity
from src.ant_client.core.executor import JobExecutor
from src.core.protocol import JobRequest
from src.ant_client.ui.tray import AntTray
from src.ant_client.ui.dashboard import AntDashboard
from src.config import settings

# Configure Logging
log_file = os.path.join(BASE_DIR, "ant_client.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("MonewmentAnt")

SERVER_URL = "ws://127.0.0.1:8000"

# --- Mock Vault for Standalone Client ---
class MockVaultDownloader:
    async def download_file(self, file_id: int, dest_dir: str) -> str:
        logger.info(f"📥 Downloading file {file_id}...")
        file_path = os.path.join(BASE_DIR, "cube.blend")
        if not os.path.exists(file_path):
             with open(file_path, "wb") as f:
                 f.write(b"DUMMY_BLEND_CONTENT")
        return file_path

class MockVaultUploader:
    async def upload_file(self, file_path: str) -> int:
        logger.info(f"📤 Uploading result {file_path}...")
        return 777

class AntWorker(threading.Thread):
    def __init__(self, client_id, token=None):
        super().__init__()
        self.client_id = client_id
        self.token = token
        self.running = True
        self.loop = None
        self.executor = JobExecutor(
            client_id=client_id,
            vault_downloader=MockVaultDownloader(),
            vault_uploader=MockVaultUploader()
        )
        self.security = AntSecurity()

    def update_token(self, token):
        self.token = token
        logger.info("🔑 Worker token updated.")

    def run(self):
        logger.info(f"🐜 Worker Thread Started: {self.client_id}")
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect_and_process())
    
    async def connect_and_process(self):
        url = f"{SERVER_URL}/ws/ant/{self.client_id}"
        import websockets
        
        while self.running:
            if not self.token:
                await asyncio.sleep(1)
                continue

            try:
                logger.info(f"Connecting to Queen with Token...")
                # Authorization header can be sent as a subprotocol or custom header if supported
                # For this MVP, we pass client_id, security handles decryption validation.
                async with websockets.connect(url) as ws:
                    logger.info("Connected to Queen!")
                    
                    while self.running and self.token:
                        payload = {"type": "heartbeat", "client_id": self.client_id, "status": "ONLINE", "token": self.token}
                        await ws.send(self.security.encrypt_payload(payload))
                        
                        try:
                            msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                            data = json.loads(msg)
                            
                            if data.get("type") == "job_request":
                                logger.info(f"⚡ Received Job: {data}")
                                job_data = data.get("data")
                                job = JobRequest(**job_data)
                                result = await self.executor.execute_job(job)
                                
                                res_payload = {
                                    "type": "job_result",
                                    "client_id": self.client_id,
                                    "data": result.dict(),
                                    "token": self.token
                                }
                                await ws.send(self.security.encrypt_payload(res_payload))
                                logger.info(f"✅ Job Finished")
                            
                            elif data.get("type") == "token_sync":
                                logger.info("🔑 Received Token Sync from Queen!")
                                self.token = data.get("token")
                                # [Phase 10] Notify app to save for silent start
                                if hasattr(self, 'on_token_received') and self.on_token_received:
                                    self.on_token_received(self.token)
                                
                        except asyncio.TimeoutError:
                            pass
                        except Exception as e:
                            logger.error(f"Loop Error: {e}")
                            
                        await asyncio.sleep(0.1)
                        
            except Exception as e:
                logger.error(f"Connection Error: {e}. Retry in 5s...")
                await asyncio.sleep(5)
                
    def stop(self):
        self.running = False

import ctypes

def ensure_single_instance():
    kernel32 = ctypes.windll.kernel32
    mutex = kernel32.CreateMutexW(None, False, "Global\\MonewmentAnt_SingleInstance_Mutex")
    if kernel32.GetLastError() == 183:
        return None
    return mutex

class MonewmentApp:
    def __init__(self):
        self.dashboard = AntDashboard(on_auth_success=self.on_auth_success)
        self.worker = None
        self.tray = None
        self.token = None

    def on_auth_success(self, token):
        logger.info("✅ Auth Success Callback triggered.")
        self.token = token
        
        # [Phase 10] Save for silent start
        config = self.dashboard.load_config()
        config["token"] = token
        self.dashboard.save_config(config)

        if not self.worker:
            self.start_worker(token)
        else:
            self.worker.update_token(token)
        
        # Transition to Dashboard view (from Login)
        self.dashboard.navigate("http://localhost:3000/admin/deepsync")
        self.dashboard.resize(1200, 800)

    def start_worker(self, token):
        self.worker = AntWorker("ant-desktop-01", token=token)
        self.worker.on_token_received = self.on_auth_success # Link callback
        self.worker.start()

    def on_exit(self):
        logger.info("🛑 Exiting App...")
        if self.worker:
            self.worker.stop()
            self.worker.join()
        sys.exit(0)

    def run(self):
        # 1. Check persistence
        config = self.dashboard.load_config()
        self.token = config.get("token")

        # 2. Setup Tray (Always runs in background)
        self.tray = AntTray(on_exit_callback=self.on_exit, dashboard=self.dashboard)
        tray_thread = threading.Thread(target=self.tray.run, daemon=True)
        tray_thread.start()

        if self.token:
            logger.info("✨ Valid Token found. Silent Start.")
            self.start_worker(self.token)
            # Start dashboard hidden or at dashboard page
            self.dashboard.start(url="http://localhost:3000/admin/deepsync", hidden=True)
        else:
            logger.info("🔑 No Token found. Launching Login Modal.")
            self.dashboard.start(url="http://localhost:3000/login?context=client", hidden=False)

def main():
    logger.info("🚀 Monewment Ant Client Starting...")
    mutex = ensure_single_instance()
    if not mutex:
        ctypes.windll.user32.MessageBoxW(0, "Monewment Ant is already running!\nCheck the System Tray.", "Monewment Ant", 0x30 | 0x1000)
        sys.exit(0)
    
    app = MonewmentApp()
    app.run()

if __name__ == "__main__":
    main()
