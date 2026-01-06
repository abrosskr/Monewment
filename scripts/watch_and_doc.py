"""
Monewment CCTV 파일 감시자 (File Watcher)
실시간으로 코드 변경을 감지하고 자동으로 문서를 생성합니다.

사용법:
    python scripts/watch_and_doc.py

종료:
    Ctrl+C
"""

import time
import os
import sys
import subprocess
from datetime import datetime

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("❌ watchdog 라이브러리가 설치되지 않았습니다.")
    print("   설치: pip install watchdog")
    sys.exit(1)

# 감시할 파일 확장자
WATCH_EXTENSIONS = {'.py', '.tsx', '.ts', '.yml', '.yaml', '.json'}

# 제외할 디렉토리
EXCLUDE_DIRS = {'__pycache__', '.git', 'node_modules', '.next', '.venv', 'dist', 'build'}

# 문서 재생성 쿨다운 (초) - 너무 자주 실행되는 것을 방지
COOLDOWN_SECONDS = 5

class CodeChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_run = 0
        self.pending_changes = []
    
    def should_process(self, path):
        """파일이 처리 대상인지 확인"""
        # 제외 디렉토리 체크
        for exclude in EXCLUDE_DIRS:
            if exclude in path:
                return False
        
        # 확장자 체크
        _, ext = os.path.splitext(path)
        return ext in WATCH_EXTENSIONS
    
    def on_modified(self, event):
        """파일 수정 이벤트 처리"""
        if event.is_directory:
            return
        
        if not self.should_process(event.src_path):
            return
        
        current_time = time.time()
        
        # 쿨다운 체크
        if current_time - self.last_run < COOLDOWN_SECONDS:
            if event.src_path not in self.pending_changes:
                self.pending_changes.append(event.src_path)
                print(f"⏳ 변경 대기 중: {os.path.basename(event.src_path)}")
            return
        
        # 문서 재생성 실행
        self.generate_docs(event.src_path)
        self.last_run = current_time
        self.pending_changes.clear()
    
    def generate_docs(self, changed_file):
        """문서 생성 스크립트 실행"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n{'='*60}")
        print(f"🔍 [{timestamp}] 변경 감지: {os.path.basename(changed_file)}")
        print(f"📝 자동 문서 생성 시작...")
        
        try:
            result = subprocess.run(
                ["python", "scripts/generate_docs_v4.py"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("✅ 문서 생성 완료!")
                if result.stdout:
                    print(result.stdout)
            else:
                print(f"❌ 문서 생성 실패 (코드: {result.returncode})")
                if result.stderr:
                    print(result.stderr)
        
        except subprocess.TimeoutExpired:
            print("⏱️  타임아웃: 문서 생성이 60초를 초과했습니다")
        except Exception as e:
            print(f"❌ 오류 발생: {str(e)}")
        
        print(f"{'='*60}\n")

def main():
    """메인 실행 함수"""
    print("👁️  Monewment CCTV 파일 감시자 시작")
    print("="*60)
    print(f"📂 감시 디렉토리: src/, gui/")
    print(f"📄 감시 확장자: {', '.join(WATCH_EXTENSIONS)}")
    print(f"⏱️  쿨다운: {COOLDOWN_SECONDS}초")
    print(f"🚫 제외 디렉토리: {', '.join(EXCLUDE_DIRS)}")
    print("="*60)
    print("💡 파일을 저장하면 자동으로 문서가 생성됩니다")
    print("🛑 종료하려면 Ctrl+C를 누르세요\n")
    
    # 감시자 설정
    event_handler = CodeChangeHandler()
    observer = Observer()
    
    # src 디렉토리 감시
    if os.path.exists("src"):
        observer.schedule(event_handler, "src", recursive=True)
        print("✅ src/ 디렉토리 감시 시작")
    
    # gui 디렉토리 감시
    if os.path.exists("gui"):
        observer.schedule(event_handler, "gui", recursive=True)
        print("✅ gui/ 디렉토리 감시 시작")
    
    # docs 디렉토리 감시 (설정 파일 등)
    if os.path.exists("docs"):
        observer.schedule(event_handler, "docs", recursive=True)
        print("✅ docs/ 디렉토리 감시 시작")
    
    observer.start()
    print("\n🟢 감시 중... (파일을 수정해보세요)\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 감시자 종료 중...")
        observer.stop()
        observer.join()
        print("✅ 정상 종료되었습니다")

if __name__ == "__main__":
    main()
