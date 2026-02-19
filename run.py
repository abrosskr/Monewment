import os
import sys
import subprocess
from src.core.config import settings

def run_step(name, command):
    print(f"--- [Step: {name}] ---")
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"!!! Error in {name}: {e} !!!")
        return False

def main():
    if not os.path.exists(".env"):
        print("CRITICAL: .env file missing.")
        sys.exit(1)
        
    print(f"\n--- Initializing Monewment V3 Engine on Port {settings.PORT_CORE_API} ---")
    run_step("Ignition", f"uvicorn src.main:app --host {settings.HOST} --port {settings.PORT_CORE_API} --reload --no-access-log")

if __name__ == "__main__":
    main()