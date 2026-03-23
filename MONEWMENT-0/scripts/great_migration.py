import os
import shutil
from pathlib import Path

# ==============================================================================
# # great_migration.py — The Great Migration (V39)
# ==============================================================================
# Role: MONEWMENT-0 코어 엔진 내부에 기생하는 하위 엔티티들을 적법한 기둥으로 강제 이주.
# ==============================================================================

MONEWMENT_0 = Path(r"c:\monewment\MONEWMENT-0")
EMPIRE_ROOT = Path(r"c:\monewment")

# Target Pillars
ANT_CODE_DIR = EMPIRE_ROOT / "ANT" / "ANT-CODE"
QUEEN_ALLY_DIR = EMPIRE_ROOT / "QUEEN" / "QUEEN_LIST" / "QUEEN-ALLY"
QUEEN_IN_DIR = EMPIRE_ROOT / "QUEEN" / "QUEEN_LIST" / "QUEEN-IN"
MONEWMENT_1_STRATUM = EMPIRE_ROOT / "MONEWMENT-1" / "STRATUM" / "STRATUM-1"
TEMPLATES_DIR = MONEWMENT_0 / "templates"

def move_entity(src: Path, dest: Path):
    if not src.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    
    if dest.exists():
        # 만약 타겟에 이미 같은 이름이 존재한다면 덮어쓰거나 합침
        print(f"  [WARN] {dest} already exists. Moving contents...")
        for item in src.iterdir():
            target_item = dest / item.name
            try:
                if target_item.exists():
                    if target_item.is_dir():
                        shutil.rmtree(target_item, ignore_errors=True)
                    else:
                        target_item.unlink(missing_ok=True)
                shutil.move(str(item), str(dest))
            except Exception as e:
                print(f"  [ERROR] Cannot move {item.name}: {e}")
        try:
            if not any(src.iterdir()):
                src.rmdir()
        except OSError:
            print(f"  [ERROR] Cannot remove directory {src.name} (locked)")
    else:
        try:
            shutil.move(str(src), str(dest))
            print(f"  [MIGRATED] {src.name} -> {dest}")
        except PermissionError:
            print(f"  [ERROR] Permission denied moving {src.name}, trying copy & delete...")
            shutil.copytree(str(src), str(dest), dirs_exist_ok=True)
            shutil.rmtree(str(src), ignore_errors=True)

def execute_migration():
    print("=== THE GREAT MIGRATION (V39) INITIATED ===")

    # 1. ANTS Migration
    source_ants = MONEWMENT_0 / "ants"
    if source_ants.exists():
        print("\n[PHASE 1] Purging ANTs from Core...")
        for ant_dir in source_ants.iterdir():
            if ant_dir.is_dir():
                # 크롤러는 ANT-CODE 로 분류
                dest = ANT_CODE_DIR / ant_dir.name
                move_entity(ant_dir, dest)
        if not any(source_ants.iterdir()):
            source_ants.rmdir()
            print("  [SUCCESS] MONEWMENT-0/ants directory eradicated.")

    # 2. QUEENS Migration
    source_queens = MONEWMENT_0 / "queens"
    if source_queens.exists():
        print("\n[PHASE 2] Evicting QUEENS from Core...")
        for queen_dir in source_queens.iterdir():
            if queen_dir.is_dir():
                q_name = queen_dir.name.upper()
                if q_name == "QUEEN-0":
                    # QUEEN-0 은 템플릿이므로 templates 로 이동
                    dest = TEMPLATES_DIR / "QUEEN-0"
                    move_entity(queen_dir, dest)
                elif "QUEEN-IN" in q_name:
                    dest = QUEEN_IN_DIR / queen_dir.name
                    move_entity(queen_dir, dest)
                else:
                    dest = QUEEN_ALLY_DIR / queen_dir.name
                    move_entity(queen_dir, dest)
        if not any(source_queens.iterdir()):
            source_queens.rmdir()
            print("  [SUCCESS] MONEWMENT-0/queens directory eradicated.")

    # 3. STRATUM-1 Migration
    source_stratum = MONEWMENT_0 / "STRATUM-1"
    if source_stratum.exists():
        print("\n[PHASE 3] Relocating STRATUM-1 to Local Government (MONEWMENT-1)...")
        # 내부 통째로 MONEWMENT-1/STRATUM/STRATUM-1 로 이동
        move_entity(source_stratum, MONEWMENT_1_STRATUM)

    print("\n=== THE GREAT MIGRATION COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    execute_migration()
