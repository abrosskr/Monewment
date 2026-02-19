import asyncio
import os
import sys
from pathlib import Path

# Add core to sys.path for local DNA execution
sys.path.append(str(Path(__file__).parent))

from core.auth.handshake import EdenvaleHandshake

async def main():
    print("[Onboarding] Initiating Handshake...")
    handshake = EdenvaleHandshake()
    success = await handshake.initiate()
    
    if success:
        print("[Onboarding] Registration Complete. Token acquired.")
    else:
        print("[Onboarding] Handshake failed.")

if __name__ == "__main__":
    asyncio.run(main())
