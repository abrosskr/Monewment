import asyncio
import os
import sys

# [CRITICAL] 경로 인식을 위해 제국 루트를 sys.path에 강제 주입
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.provisioner import Provisioner
    from core.database import engine
except ImportError as e:
    print(f"[!] Core Module Import Failed: {e}")
    print("Ensure you are running this in c:\\monewment and dependencies are installed.")
    sys.exit(1)

async def execute_redemption():
    print("==================================================")
    print(" 🚨 MONEWMENT CORE REDEMPTION PROTOCOL INITIATED 🚨")
    print("==================================================")
    
    try:
        print("\n[*] Injecting Imperial Registry (v2.0)...")
        await Provisioner.create_registry_space()
        
        print("[*] Injecting System Control Space...")
        await Provisioner.create_system_space()
        
        print("[*] Injecting REX/AREUM Pipeline Space...")
        await Provisioner.create_pipeline_space()
        
        print("[*] Injecting PIM (Normalization) Space...")
        await Provisioner.create_pim_space()
        
        print("[*] Injecting Eternal Archive Space...")
        await Provisioner.create_archive_space()
        
        print("[*] Injecting Absolute Intelligence (REX) Space...")
        await Provisioner.create_rex_space()
        
        print("\n✅ [SUCCESS] All Neural Pathways (DB Schemas) Reconstructed.")
        
    except Exception as e:
        print(f"\n❌ [CRITICAL FAILURE] Redemption Interrupted: {e}")
    finally:
        # 안전한 커넥션 종료
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(execute_redemption())