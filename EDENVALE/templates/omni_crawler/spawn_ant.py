import os
import shutil
import json
from pathlib import Path

class AntSpawner:
    """
    [The Local Worker Spawner: spawn_ant.py]
    Resides in QUEEN. Spawns personalized ANT workers.
    """
    def __init__(self, master_ref: str = "C:/monewment/EDENVALE"):
        self.master_dir = Path(master_ref)
        self.queen_dir = Path(__file__).parent
        
    def get_dir_size(self, path: Path) -> int:
        return sum(f.stat().st_size for f in path.glob('**/*') if f.is_file())

    def spawn(self, name: str, user_id: str = "GUEST", device: str = "PC", model: str = "GEMINI"):
        # 1. Naming Engine (Worker Level)
        # Format: {USER}_{DEVICE}_{MODEL} or custom
        ant_id = name or f"{user_id}_{device}_{model}"
        ant_path = self.queen_dir / "ants" / ant_id
        
        print(f"[QUEEN] Spawning Worker: {ant_id}")
        
        if ant_path.exists(): shutil.rmtree(ant_path)
        ant_path.mkdir(parents=True)

        # 2. Pruned Inheritance
        template_src = self.master_dir / "templates" / "ant_0"
        shutil.copytree(template_src, ant_path, dirs_exist_ok=True)
        # Copy minimal core DNA
        (ant_path / "core").mkdir()
        shutil.copy(self.master_dir / "core" / "logging.py", ant_path / "core" / "logging.py")

        # 3. Path Isolation: data/buffer/[ANT_ID]
        buffer_path = ant_path / "data" / "buffer"
        buffer_path.mkdir(parents=True, exist_ok=True)

        # 4. DNA Injection
        info = {
            "ID": ant_id,
            "USER": user_id,
            "DEVICE": device,
            "MODEL": model,
            "PARENT_QUEEN": self.queen_dir.name,
            "GENESIS": "V3.0_WORKER"
        }
        with open(ant_path / ".dna", "w") as f: json.dump(info, f, indent=4)

        # 5. Verification: Size Threshold (< 5%)
        master_size = self.get_dir_size(self.master_dir)
        ant_size = self.get_dir_size(ant_path)
        ratio = (ant_size / master_size) * 100
        
        print(f"[Verification] Size: {ant_size} bytes ({ratio:.2f}% of Master)")
        if ratio > 5.0:
            print("WARNING: Pruning insufficient (> 5%)")
        else:
            print("[Verification] Extreme Pruning Confirmed.")

if __name__ == "__main__":
    import sys
    # Usage: python spawn_ant.py [Name] [User] [Device] [Model]
    spawner = AntSpawner()
    arg_name = sys.argv[1] if len(sys.argv) > 1 else None
    arg_user = sys.argv[2] if len(sys.argv) > 2 else "USER"
    arg_dev = sys.argv[3] if len(sys.argv) > 3 else "AP"
    arg_mdl = sys.argv[4] if len(sys.argv) > 4 else "V1"
    spawner.spawn(arg_name, arg_user, arg_dev, arg_mdl)
