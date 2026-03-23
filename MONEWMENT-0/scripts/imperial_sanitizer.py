import os
from pathlib import Path
import asyncio
import sys

# Path fix for AuditLogger
sys.path.insert(0, str(Path(r"c:\monewment\MONEWMENT-0")))
from core.audit_logger import AuditLogger

# ==============================================================================
# # imperial_sanitizer.py — THE CONSTITUTIONAL SANITIZER
# ==============================================================================
# Role: 전 제국 영토의 .env 파일을 스캔하여, 13대 제국 헌법에 위배되는 
#       분산형 AI 키(OLLAMA_API_KEY, OPENAI_API_KEY 등)를 적발하고 소거함.
# ==============================================================================

TARGET_ROOT = Path(r"c:\monewment")
FORGER_ROOT = Path(r"c:\forager")

# 적발 대상 (HERESY - 이단적 설정)
HERETIC_KEYS = [
    "OLLAMA_API_KEY",
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "ANTHROPIC_API_KEY",
    "OLLAMA_KEY",
    "AI_KEY",
    "LLM_KEY"
]

def sanitize_env(file_path: Path):
    if not file_path.exists():
        return
    
    print(f"[AUDIT] Scanning: {file_path}")
    lines = file_path.read_text(encoding="utf-8").splitlines()
    new_lines = []
    purged_count = 0

    for line in lines:
        is_heretic = False
        for key in HERETIC_KEYS:
            if line.strip().startswith(key + "="):
                print(f"  [PURGE] Heretic key detected: {key}")
                is_heretic = True
                purged_count += 1
                break
        
        if not is_heretic:
            new_lines.append(line)
    
    if purged_count > 0:
        file_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        print(f"  [SUCCESS] {purged_count} heretic keys scrubbed from {file_path.name}")
        
        # [DECREE 13] 산청 완료 이력 기록
        asyncio.run(AuditLogger.log_movement(
            action_type="SANITIZE-ENV",
            source=str(file_path),
            count=purged_count,
            reason="Constitutional Compliance: Removing unauthorized AI keys"
        ))
    else:
        print(f"  [CLEAN] No constitutional violations found.")

def run_sanitizer():
    print("=== Imperial Sanitizer Active (Defense by Design) ===")
    
    # 1. c:\monewment 하위 스캔
    for root, dirs, files in os.walk(TARGET_ROOT):
        for file in files:
            if file == ".env":
                sanitize_env(Path(root) / file)
                
    # 2. c:\forager 스캔
    if FORGER_ROOT.exists():
        for root, dirs, files in os.walk(FORGER_ROOT):
            for file in files:
                if file == ".env":
                    sanitize_env(Path(root) / file)

    print("\n=== Imperial Sanctity Restored. All .env files compliant with 13 Decrees. ===")

if __name__ == "__main__":
    run_sanitizer()
