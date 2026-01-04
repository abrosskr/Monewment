import os
import time
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# === 설정 ===
WATCH_DIR = "docs/specs"
OUTPUT_DIR = "gui/components"

class UIHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".json"):
            self.generate_code(event.src_path)

    def on_created(self, event):
        if event.src_path.endswith(".json"):
            self.generate_code(event.src_path)

    def generate_code(self, file_path):
        try:
            # [수정] encoding="utf-8-sig"를 사용하여 윈도우 BOM 문제 해결
            with open(file_path, "r", encoding="utf-8-sig") as f:
                schema_data = json.load(f)

            filename = os.path.basename(file_path).replace(".json", "")
            comp_name = filename[0].upper() + filename[1:]

            print(f"\n[UI Factory] ⚡ JSON 설계도 감지: {filename}.json")

            tsx_code = f"""'use client';
import UIRenderer from '@/components/ui-engine/Renderer';

// [Auto-Generated] Server-Driven UI Schema
const SCHEMA = {json.dumps(schema_data, indent=2, ensure_ascii=False)};

export default function {comp_name}() {{
  return <UIRenderer schema={{SCHEMA}} />;
}}
"""
            output_path = os.path.join(OUTPUT_DIR, f"{comp_name}.tsx")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(tsx_code)
            
            print(f"[Success] ✅ 컴포넌트 생성 완료! -> {output_path}")

        except json.JSONDecodeError:
            print(f"[Error] JSON 형식이 올바르지 않습니다: {file_path}")
        except Exception as e:
            print(f"[Error] 변환 실패: {e}")

if __name__ == "__main__":
    if not os.path.exists(WATCH_DIR):
        os.makedirs(WATCH_DIR)
    
    event_handler = UIHandler()
    observer = Observer()
    observer.schedule(event_handler, path=WATCH_DIR, recursive=False)
    observer.start()

    print(f"🧱 [UI Factory] JSON 엔진 가동 중... '{WATCH_DIR}' 폴더를 감시합니다.")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt: observer.stop()
    observer.join()
