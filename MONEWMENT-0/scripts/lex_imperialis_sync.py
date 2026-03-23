import os
import shutil
import json
from pathlib import Path

# ==============================================================================
# # lex_imperialis_sync.py — Lex Imperialis (V44) Top-Down Sync Script
# ==============================================================================
# Role: MONEWMENT-0에서 허가된 하위 영토로만 헌법을 안전하게 배포.
# [V44] 1. 절대적 코어 방어 칙령 도입: 불필요한 재귀 스캔(rglob)을 삭제하고 오직 승인된 영토만 스캔.
# [V44] 2. 계층 매핑: 하위 경로의 성격에 맞춰 .stratum, .queen, .ant, .areum, .rex 폴더명으로 배포.
# ==============================================================================

# 절대 기준점 (Master)
ROOT_DIR = Path(r"c:\monewment")
MASTER_EDEN_DIR = ROOT_DIR / ".eden"

# [V44 코어 불가침] 승인된 외부 영토 및 기둥 루트만 전파 풀에 둔다.
# MONEWMENT-0 내부 스캔은 절대 금지.
APPROVED_TERRITORIES = [
    # 8 Pillars
    ROOT_DIR / "QUEEN",
    ROOT_DIR / "ANT",
    ROOT_DIR / "STRATUM",
    ROOT_DIR / "AREUM",
    ROOT_DIR / "REX",
    ROOT_DIR / "sfis",
    # Leaf Services
    Path(r"c:\forager"),
    Path(r"c:\physics"),
    Path(r"c:\recilabeler"),
    Path(r"c:\areum"),
    Path(r"c:\edenvale")
]

def get_pillar_type(target_path: Path) -> str:
    """타겟 경로의 성격을 분석하여 매핑할 도트 폴더명을 반환합니다."""
    name = target_path.name.upper()

    if "QUEEN" in name:
        return ".queen"
    elif "ANT" in name or "FORAGER" in name:
        return ".ant"
    elif "AREUM" in name or "RECILABELER" in name:
        return ".areum"
    elif "REX" in name:
        return ".rex"
    elif "PHYSICS" in name or "STRATUM" in name:
        return ".stratum"
    
    return ".stratum"

def get_targets() -> set[Path]:
    """경로 스캔을 통해 전파 대상 영토를 확보 (1-Depth Only)"""
    targets = set()
    for root in APPROVED_TERRITORIES:
        if root.exists() and root.is_dir():
            targets.add(root.resolve())
            # 기둥 하위의 개별 개체(예: c:\monewment\QUEEN\QUEEN-0)까지 1-Depth만 탐색
            if root.parent == ROOT_DIR:
                for sub in root.iterdir():
                    if sub.is_dir():
                        targets.add(sub.resolve())
    return targets

def purge_redundant_files(target: Path):
    """
    [Lex Imperialis V44]
    기존에 잘못 복사된 파일 제거. (코어 폴더는 아예 targets 목록에 없으므로 안전)
    """
    for bad_file in [".gemini_instructions.md", "gemini_instructions.md"]:
        f = target / bad_file
        if f.exists() and f.is_file():
            f.unlink()
            print(f"  [PURGE] Destroyed redundant instruction: {f}")

    legacy_eden = target / ".eden"
    if legacy_eden.exists() and legacy_eden.is_dir():
        shutil.rmtree(legacy_eden)
        print(f"  [PURGE] Eradicated legacy constitution folder: {legacy_eden}")

def sync_path(src: Path, dst: Path):
    if not src.exists(): return
    if dst.exists():
        if dst.is_dir():
            shutil.rmtree(dst)
        else:
            dst.unlink()

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    print(f"  [DIR]  {src.name}/ -> {dst}/")

def propagate():
    print("=== Lex Imperialis v44: Top-Down Constitution Sync (Safe Mode) ===")
    
    if not MASTER_EDEN_DIR.exists():
        print(f"[FATAL] Master Constitution not found at {MASTER_EDEN_DIR}")
        return

    targets = get_targets()
    print(f"Detected Approved Territories: {[t.name for t in targets]}")
    
    sync_ver = "LEX_IMPERIALIS_V44"

    for target in targets:
        print(f"\n[TARGET] {target.name} ({target})")
        
        purge_redundant_files(target)
        
        pillar_dot_folder = get_pillar_type(target)
        target_eden_dir = target / pillar_dot_folder
        
        sync_path(MASTER_EDEN_DIR, target_eden_dir)
        
        dna_path = target / "dna.lock"
        try:
            dna = {}
            if dna_path.exists():
                with open(dna_path, "r", encoding="utf-8") as f:
                    dna = json.load(f)
            
            dna["last_broadcast_sync"] = "2026-02-28T17:00:00"
            dna["imperial_version"] = "4.4-LEX-IMPERIALIS"
            dna["decrees_applied"] = "15_DECREES_V44"
            dna["sync_id"] = sync_ver
            dna["constitutional_binding"] = pillar_dot_folder
            dna["core_inviolability"] = "ACKNOWLEDGED"
            
            with open(dna_path, "w", encoding="utf-8") as f:
                json.dump(dna, f, indent=4)
            print(f"  [LOCK] dna.lock secured: Bound to {pillar_dot_folder}")
        except Exception as e:
            print(f"  [WARN] Failed to secure dna.lock: {e}")

    print("\n=== Imperial Ecosystem Purged and Synchronized with V44 ===")

if __name__ == "__main__":
    propagate()
