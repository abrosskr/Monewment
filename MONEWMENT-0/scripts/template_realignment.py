import os
import shutil
from pathlib import Path

def main():
    print("=== [V42] Imperial Template Realignment ===")
    
    empire_root = Path(r"C:\monewment")
    src_templates_dir = empire_root / "MONEWMENT-0" / "templates"
    
    # Define mapping: source_folder -> destination_folder
    # According to 14_STRUCTURE.md, pillars are: ANT, QUEEN, AREUM, STRATUM
    mappings = {
        "ANT-0": empire_root / "ANT" / "ANT-0",
        "QUEEN-0": empire_root / "QUEEN" / "QUEEN-0",
        "AREUM-0": empire_root / "AREUM" / "AREUM-0",
        "STRATUM-0": empire_root / "STRATUM" / "STRATUM-0",
        "AREUM-IN-1": empire_root / "AREUM" / "AREUM-IN-1" # Also found in templates
    }
    
    if not src_templates_dir.exists():
        print(f"FAILED: Source directory does not exist: {src_templates_dir}")
        return
        
    for template_name, dest_path in mappings.items():
        src_path = src_templates_dir / template_name
        
        if not src_path.exists():
            print(f"[-] Source template {template_name} does not exist. Skipping.")
            continue
            
        print(f"[*] Relocating {template_name}...")
        print(f"    From: {src_path}")
        print(f"    To:   {dest_path}")
        
        try:
            # If destination already exists, we might need to merge or overwrite.
            # Shutil.copytree can merge in python 3.8+ using dirs_exist_ok=True
            shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
            print(f"    -> Copied successfully to target.")
            
            # Remove source after successful copy (safer than direct move across drives sometimes, though it's same drive here)
            shutil.rmtree(src_path)
            print(f"    -> Eradicated source folder: {src_path}")
        except Exception as e:
            print(f"    -> FAILED to relocate {template_name}: {e}")

if __name__ == "__main__":
    main()
