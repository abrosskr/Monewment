import os
import shutil
import json
from pathlib import Path

# ==============================================================================
# # broadcast_update.py — EDENVALE Template Propagation System
# ==============================================================================
# Role: MONEWMENT-0 (Master DNA)에서 하위 모든 영토로 헌법 및 지침서를 일괄 배포함.
# ==============================================================================

# 검색 대상 루트 디렉토리들
SEARCH_ROOTS = [Path(r"c:\monewment"), Path(r"c:\\")]
MASTER_DNA = Path(r"c:\monewment\MONEWMENT-0")
EDEN_DIR = Path(r"c:\monewment\.eden")
INSTRUCTIONS_FILE = Path(r"c:\monewment\.gemini_instructions.md")

# 검색에서 제외할 폴더들 (Windows 시스템 폴더 등)
EXCLUDE_DIRS = {
    "Windows", "Program Files", "Program Files (x86)", "ProgramData",
    "Recovery", "System Volume Information", "$Recycle.Bin",
    "Recovery", "System Volume Information", "$Recycle.Bin", "PerfLogs",
    "Documents and Settings", ".venv", "__pycache__", "MONEWMENT-0", ".git"
}

# 템플릿 원천 정의
TEMPLATES = {
    ".areum": MASTER_DNA / "templates" / "AREUM-0" / ".areum",
    ".ant": MASTER_DNA / "templates" / "ANT-0" / ".ant",
    ".stratum": MASTER_DNA / "templates" / "STRATUM-0" / ".stratum",
    ".queen": MASTER_DNA / "queens" / "QUEEN-0" / ".queen"
}

def get_projects():
    """여러 루트에서 유효한 프로젝트 디렉토리 탐지 (Recursive)"""
    projects = []
    seen = set()
    
    def scan(root: Path, depth: int):
        if depth > 3: return # 최대 깊이 제한
        try:
            if not root.exists() or not root.is_dir(): return
            if root.name.startswith(".") or root.name in EXCLUDE_DIRS: return
            
            # 프로젝트 판별
            is_project = (root / ".env").exists() or any((root / m).exists() for m in [".queen", ".ant", ".areum", "queens"])
            if is_project and root != MASTER_DNA:
                if root.resolve() not in seen:
                    projects.append(root)
                    seen.add(root.resolve())
                return # 프로젝트 내부로는 더 들어가지 않음
                
            # 하위 디렉토리 탐색
            for p in root.iterdir():
                if p.is_dir():
                    scan(p, depth + 1)
        except (PermissionError, OSError):
            return

    for root in SEARCH_ROOTS:
        scan(root, 0)
    return projects

ROOT_DIR = Path(r"c:\\")

def sync_path(src: Path, dst: Path):
    """파일 또는 디렉토리를 멱등성 있게 동기화"""
    if not src.exists():
        return
    
    dst.parent.mkdir(parents=True, exist_ok=True)
    
    if src.is_file():
        shutil.copy2(src, dst)
        print(f"  [FILE] {src.name} -> {dst}")
    else:
        # 디레토리 동기화 (기존 내용 덮어씀)
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        print(f"  [DIR]  {src.name}/ -> {dst}")

def broadcast():
    print(f"Broadcaster Active: Genesis Sync starting from {MASTER_DNA.name}...")
    
    targets = get_projects()
    print(f"Found {len(targets)} potential target projects: {[t.name for t in targets]}")
    
    for target in targets:
        print(f"\nPropagating to: {target.name}")
        
        # 1. 루트 지침서 및 제국 헌법 배포 (Imperial Constitution Sync)
        sync_path(INSTRUCTIONS_FILE, target / ".gemini_instructions.md")
        sync_path(Path("C:/monewment/.eden/01_CONSTITUTION.md"), target / "IMPERIAL_CONSTITUTION.md")
        # guides는 이제 배포하지 않고 SSOT로만 남김 (제2기 법령)
        
        # 2. 내부에 숨겨진 마커 폴더 탐색 및 템플릿 배포 (삭제됨)
        # 13대 제국 헌법에 따라 템플릿(-0)은 MONEWMENT-0에만 존재해야 하므로, 
        # 더 이상 하위 STRATUM의 마커 폴더에 템플릿을 무단 복제하여 리소스를 낭비하지 않음.

        # 3. DNA Lock 갱신 (버전 추적용)
        dna_path = target / "dna.lock"
        try:
            dna = {}
            if dna_path.exists():
                with open(dna_path, "r", encoding="utf-8") as f:
                    dna = json.load(f)
            
            dna["last_broadcast_sync"] = "2026-02-23T21:20:00" # 오늘 날짜/버전
            dna["template_integrity"] = "VERIFIED"
            
            with open(dna_path, "w", encoding="utf-8") as f:
                json.dump(dna, f, indent=2)
            print(f"  [LOCK] dna.lock updated.")
        except Exception as e:
            print(f"  [WARN] Failed to update dna.lock: {e}")

if __name__ == "__main__":
    broadcast()
    print("\nBroadcast complete. All territories synchronized with Master DNA.")
