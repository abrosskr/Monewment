import sys
import json
import os
import platform
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict

MANIFEST_PATH = Path(__file__).parents[1] / "vess_manifest.json"

def get_critical_packages() -> Dict[str, str]:
    """
    Identify critical packages.
    In a strict mode, this might be EVERYTHING in freeze.
    For this implementation, we lock EVERYTHING that is explicitly in requirements.txt
    OR we can just lock the current state as the law.
    Control Plane Policy: The current 'stabilized' state is the Law. So we lock what is installed.
    """
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True, check=True)
        packages = {}
        for line in result.stdout.splitlines():
            if "==" in line:
                name, version = line.split("==", 1)
                packages[name.lower()] = version
        return packages
    except subprocess.CalledProcessError:
        print("Error: Failed to run pip freeze")
        sys.exit(1)

def lock_environment():
    """Generate manifest from current environment."""
    print("🔒 Locking Monewment Environment definition...")
    
    current_python = platform.python_version()
    # Lock to Major.Minor to allow patch updates if needed, or strict. 
    # Policy says "3.11.x" in plan due to 3.11.9
    python_policy = ".".join(current_python.split(".")[:2]) + "." # 3.11.
    
    installed = get_critical_packages()
    
    manifest = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "generated_by": "VESS_LOCKER",
            "policy": "STRICT"
        },
        "python_version": python_policy, 
        "node_version": "LTS", # Placeholder for now, can implement node check later
        "critical_dependencies": installed
    }
    
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"✅ VESS Manifest generated at: {MANIFEST_PATH}")
    print(f"   Python: {current_python}")
    print(f"   Packages Locked: {len(installed)}")

if __name__ == "__main__":
    lock_environment()
