import sys
import json
import os
import platform
import subprocess
from pathlib import Path
from typing import Dict, Any, List

MANIFEST_PATH = Path(__file__).parents[1] / "vess_manifest.json"

def get_installed_packages() -> Dict[str, str]:
    """Get currently installed packages using pip freeze."""
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True, check=True)
        packages = {}
        for line in result.stdout.splitlines():
            if "==" in line:
                name, version = line.split("==", 1)
                packages[name.lower()] = version
            elif "@" in line: # Handle direct references if any
                 pass 
        return packages
    except subprocess.CalledProcessError:
        print("Error: Failed to run pip freeze")
        sys.exit(1)

def check_environment() -> Dict[str, Any]:
    """Compare current environment against manifest."""
    if not MANIFEST_PATH.exists():
        return {
            "status": "FAIL",
            "error": "Manifest file not found (vess_manifest.json). System is UNGOVERNED."
        }
    
    try:
        with open(MANIFEST_PATH, "r") as f:
            manifest = json.load(f)
    except json.JSONDecodeError:
         return {
            "status": "FAIL",
            "error": "Manifest file is corrupted JSON."
        }

    drift = []
    
    # 1. Python Version Check
    required_python = manifest.get("python_version", "")
    current_python = platform.python_version()
    
    # Simple major.minor check for now, can be stricter
    if not current_python.startswith(required_python.rstrip("x")):
         drift.append(f"Python Integrity Violation: Expected {required_python}, Found {current_python}")
         
    # 2. Dependencies Check
    installed = get_installed_packages()
    critical_deps = manifest.get("critical_dependencies", {})
    
    for pkg, req_version in critical_deps.items():
        pkg_key = pkg.lower()
        if pkg_key not in installed:
            drift.append(f"Missing Critical Dependency: {pkg}")
        elif installed[pkg_key] != req_version:
             drift.append(f"Version Drift: {pkg} Expected {req_version}, Found {installed[pkg_key]}")

    if drift:
        return {
            "status": "FAIL",
            "drift": drift,
            "manifest_version": manifest.get("meta", {}).get("generated_at", "Unknown")
        }
    
    return {
        "status": "PASS",
        "description": "Environment matches VESS Law."
    }

if __name__ == "__main__":
    report = check_environment()
    print(json.dumps(report, indent=2))
    if report["status"] != "PASS":
        sys.exit(1)
    sys.exit(0)
