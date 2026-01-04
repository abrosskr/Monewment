import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .manager import DevToolsManager

class ProWatcher(FileSystemEventHandler):
    def __init__(self, root_dir):
        self.manager = DevToolsManager(root_dir)
        self.last_run = 0

    def on_any_event(self, event):
        # 중복 실행 방지 및 문서 폴더 제외
        if time.time() - self.last_run < 1.0: return
        if "docs" in event.src_path or "__pycache__" in event.src_path: return
        
        self.last_run = time.time()
        print(f"⚡ [감지] {os.path.basename(event.src_path)} 변경됨 -> 4대 엔진 가동!")
        
        self.manager.run_all_inspections()
        print("✅ [완료] 문서 최신화 끝.")

def start_watching(root_dir):
    print(f"🔭 Monewment PRO Watcher 가동 (Path: {root_dir})")
    print("   - 감시 항목: 구조, 데이터, 통신, 설정 (All-in-One)")
    
    # [최적화] 최초 실행 시 사용자에게 진행 상황을 알림 (Silent 모드 해제)
    print("   👉 초기 스캔 및 문서화 진행 중...", end="", flush=True)
    
    # 한 번 싹 정리
    DevToolsManager(root_dir).run_all_inspections()
    
    print(" [완료!]")
    print("   ✅ 이제 파일이 변경되면 자동으로 감지합니다. (Ctrl+C로 종료)")
    
    observer = Observer()
    observer.schedule(ProWatcher(root_dir), root_dir, recursive=True)
    observer.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()