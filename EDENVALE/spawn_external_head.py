import os
import shutil
import json
import secrets
from pathlib import Path

class ExternalSpawner:
    """
    [The Absolute Path Spawner]
    Deploys specialized instances outside the local hierarchy.
    """
    def __init__(self, master_dir: str = "C:/monewment/EDENVALE"):
        self.master_dir = Path(master_dir)
        self.onboarding_package = self.master_dir / "dna" / "onboarding_package"

    def spawn(self, target_path_str: str, instance_id: str):
        target_path = Path(target_path_str)
        if target_path.exists():
            print(f"Warning: Target path {target_path} already exists. Overwriting...")
            shutil.rmtree(target_path)
            
        target_path.mkdir(parents=True)
        print(f"[Genesis] External Spawning: {instance_id} -> {target_path}")

        # 1. Force-Inject Onboarding DNA
        dest_core = target_path / "core"
        dest_core.mkdir(parents=True)
        for item in ["protocol", "auth", "monitor"]:
            src = self.onboarding_package / item
            dst = dest_core / item
            shutil.copytree(src, dst)
            
        # Copy bootstrap script
        shutil.copy(self.onboarding_package / "bootstrap_handshake.py", target_path / "handshake.py")

        # 2. Inject Template
        shutil.copy(self.master_dir / "templates" / "ant_0" / "main.py", target_path / "main.py")

        # 3. Environment Provisioning
        instance_key = secrets.token_hex(32)
        env_content = f"""MASTER_API_URL=http://localhost:8201
INSTANCE_ID={instance_id}
INSTANCE_KEY={instance_key}
LAYER=EXTERNAL
"""
        with open(target_path / ".env", "w", encoding="utf-8") as f:
            f.write(env_content)

        # 4. Success Signaling
        print(f"[Genesis] External Instance {instance_id} born at {target_path}")
        print(f"[Security] Instance Key Generated: {instance_key}")

if __name__ == "__main__":
    import sys
    spawner = ExternalSpawner()
    if len(sys.argv) > 2:
        spawner.spawn(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python spawn_external_head.py <absolute_path> <instance_id>")
