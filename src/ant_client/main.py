from pathlib import Path
from src.ant_client.core.watchdog import Watchdog
from src.ant_client.core.updater import Updater
import os

def main():
    print("🚀 Launching Monewment Ant Client (Enterprise Edition)")
    
    # [OTA] Check for updates on startup
    # In real world, read URL from config file or env
    server_url = os.getenv("QUEEN_SERVER_URL", "http://localhost:8000")
    current_version = "1.0.0" # Should be read from a version file
    
    updater = Updater(server_url, current_version)
    updater.check_and_update() # Will restart if update successful
    
    current_dir = Path(__file__).parent
    worker_script = current_dir / "worker_main.py"
    
    dog = Watchdog(str(worker_script))
    dog.monitor()

if __name__ == "__main__":
    main()
