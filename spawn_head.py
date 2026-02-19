import os
import sys
import shutil
import json
import subprocess
from pathlib import Path

class Spawner:
    """
    [MONEWMENT Spawner: Codex Edition]
    Enforces the Level 0 -> Level 3 hierarchy.
    Usage: python spawn_head.py --stratium 1 --queen CRAWLER --ant PHS_PC_01
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.prime_dir = base_dir / "monewment_0"
        self.dna_path = self.prime_dir / "dna" / "dna_manifest.json"

    def spawn_ant(self, stratium_n: int, queen_name: str, ant_id: str):
        print(f"--- Spawning ANT: {ant_id} in {queen_name} (STRATIUM-{stratium_n}) ---")
        
        # 1. Path Calculation (The Codex Law)
        stratium_dir = self.base_dir / f"STRATIUM-{stratium_n}"
        queen_dir = stratium_dir / f"QUEEN_{queen_name}"
        ant_dir = queen_dir / "ants" / ant_id
        
        print(f"Target Path: {ant_dir.relative_to(self.base_dir)}")
        
        # 2. Duplicate DNA (Level 0 -> Level 3)
        if ant_dir.exists():
            print(f"Ant {ant_id} already exists. Cleaning...")
            shutil.rmtree(ant_dir)
        
        ant_dir.mkdir(parents=True, exist_ok=True)
        # Copy everything from monewment_0 except dna/ (optional, usually specs are kept)
        for item in os.listdir(self.prime_dir):
            s = self.prime_dir / item
            d = ant_dir / item
            if s.is_dir():
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

        # 3. Setup Virtual Environment
        venv_name = f"venv_{ant_id.lower()}"
        venv_dir = ant_dir / venv_name
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
        
        # 3.5 Install Requirements
        pip_path = venv_dir / ("Scripts" if os.name == "nt" else "bin") / "pip"
        req_path = ant_dir / "requirements.txt"
        if req_path.exists():
            subprocess.run([str(pip_path), "install", "-r", str(req_path)], check=True)

        # 5. Context Injection (.env)
        env_content = f"""
STRATIUM_ID=STRATIUM-{stratium_n}
QUEEN_ID=QUEEN_{queen_name}
ANT_ID={ant_id}
MASTER_API=http://127.0.0.1:8201
"""
        with open(ant_dir / ".env", "w") as f:
            f.write(env_content.strip())
            
        # 6. 가상환경에 ANT 루트 경로 영구 등록 (.pth Injection)
        site_packages_dir = venv_dir / "Lib" / "site-packages" if os.name == "nt" else \
                            venv_dir / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
        
        if site_packages_dir.exists():
            with open(site_packages_dir / "monewment.pth", "w") as f:
                f.write(str(ant_dir.resolve()))
            print(f"[OK] Path registered in venv: {ant_dir}")
        else:
            print(f"[WARN] Could not find site-packages in {venv_dir}. .pth skip.")

        print(f"[OK] ANT Spawned and Context Injected.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--stratium", type=int, default=1)
    parser.add_argument("--queen", type=str, default="DEFAULT")
    parser.add_argument("--ant", type=str, required=True)
    
    args = parser.parse_args()
    
    base = Path("C:/monewment")
    spawner = Spawner(base)
    spawner.spawn_ant(args.stratium, args.queen, args.ant)
