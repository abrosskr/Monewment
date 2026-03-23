import os
import time
import sys
from datetime import datetime

# CCTV Monitor: Unified Log Feed
LOG_DIR = "logs/imperial"

def tail_logs():
    print(f"[{datetime.now()}] 📡 [CCTV] Initializing Imperial Unified Feed...")
    print("="*60)
    
    # Track file positions
    positions = {}
    
    while True:
        if not os.path.exists(LOG_DIR):
            print(f"[{datetime.now()}] [CCTV] Waiting for LOG_DIR to be created...")
            time.sleep(2)
            continue
            
        files = [f for f in os.listdir(LOG_DIR) if f.endswith(".log")]
        
        for filename in files:
            path = os.path.join(LOG_DIR, filename)
            ant_id = filename.replace(".log", "")
            
            # Open file if not tracked
            if path not in positions:
                print(f"[{datetime.now()}] 👁️ [NEW_FEED] Found {ant_id}")
                positions[path] = os.path.getsize(path) # Start from current end
            
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                f.seek(positions[path])
                new_data = f.read()
                if new_data:
                    for line in new_data.splitlines():
                        if line.strip():
                            # Format for readability
                            print(f"[{ant_id}] {line.strip()}")
                    positions[path] = f.tell()
        
        time.sleep(0.5) # Fast polling for 'Live' feel

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--clear":
            import shutil
            if os.path.exists(LOG_DIR):
                shutil.rmtree(LOG_DIR)
                print("[CCTV] Log directory cleared.")
                
        tail_logs()
    except KeyboardInterrupt:
        print("\n[CCTV] Feed disconnected. System remains active.")
