import os
import shutil
from pathlib import Path

def consolidate_territory(source_dir, dest_dir, new_name, queen_id, stratum_id):
    source = Path(source_dir)
    dest = Path(dest_dir)
    
    print(f"Consolidating {source} -> {dest}...")
    
    if not source.exists():
        print(f"  [SKIP] Source {source} not found.")
        return False

    # 1. Create dest if not exists
    if not dest.exists():
        dest.mkdir(parents=True)
    
    # 2. Sync files (Source of truth is source_dir)
    for item in os.listdir(source):
        s_item = source / item
        d_item = dest / item
        if s_item.is_dir():
            if d_item.exists():
                shutil.rmtree(d_item)
            shutil.copytree(s_item, d_item)
        else:
            shutil.copy2(s_item, d_item)
    
    # 3. Calibrate .env
    env_file = dest / ".env"
    if env_file.exists():
        lines = env_file.read_text("utf-8").splitlines()
        new_lines = []
        for line in lines:
            if line.startswith("STRATUM_ID="):
                new_lines.append(f"STRATUM_ID={stratum_id}")
            elif line.startswith("QUEEN_ID="):
                new_lines.append(f"QUEEN_ID={queen_id}")
            elif line.startswith("PHYSICS_NAME="):
                new_lines.append(f"PHYSICS_NAME={new_name}")
            elif line.startswith("AREUM_NAME="):
                new_lines.append(f"AREUM_NAME={new_name}")
            else:
                new_lines.append(line)
        env_file.write_text("\n".join(new_lines), "utf-8")
        print(f"  [OK] .env calibrated in {dest}")
    
    return True

if __name__ == "__main__":
    PRIMARY_QUEEN_ID = 'ba537759-f607-4eda-841c-eeba65a5147b'
    STRATUM_ID = '3bb565af-e01a-49b8-af27-049e6a642f2d'
    
    # Consolidate PHYSICS
    consolidate_territory(
        r"C:\monewment\PHYSICS\PHYSICS-3", 
        r"C:\monewment\PHYSICS\PHYSICS-1", 
        "PHYSICS", 
        PRIMARY_QUEEN_ID, 
        STRATUM_ID
    )
    
    # Consolidate AREUM
    consolidate_territory(
        r"C:\monewment\AREUM\AREUM-3", 
        r"C:\monewment\AREUM\AREUM-1", 
        "AREUM-1", 
        PRIMARY_QUEEN_ID, 
        STRATUM_ID
    )

    # Cleanup Duplicates
    to_delete = [
        r"C:\monewment\PHYSICS\PHYSICS-2",
        r"C:\monewment\PHYSICS\PHYSICS-3",
        r"C:\monewment\AREUM\AREUM-3",
        r"C:\monewment\AREUM\AREUM-FORAGER-1"
    ]
    
    for d in to_delete:
        dp = Path(d)
        if dp.exists() and dp.resolve() not in [Path(r"C:\monewment\PHYSICS\PHYSICS-1").resolve(), Path(r"C:\monewment\AREUM\AREUM-1").resolve()]:
            print(f"  [CLEANUP] Removing {dp}...")
            shutil.rmtree(dp, ignore_errors=True)
