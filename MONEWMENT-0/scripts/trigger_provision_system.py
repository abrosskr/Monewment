import asyncio
import sys
import os

# MONEWMENT-0 경로 추가
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

from core.provisioner import Provisioner

async def run_provision():
    print("=== [PROVISIONING] Manually creating system space ===")
    await Provisioner.create_system_space()
    print("[SUCCESS] System space provisioned.")

if __name__ == "__main__":
    asyncio.run(run_provision())
