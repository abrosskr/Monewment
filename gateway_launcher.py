import os
import subprocess

# 우리가 띄울 Next.js 주소
URL = "http://localhost:3000"

def launch():
    # MS Edge의 '앱 모드'를 사용하여 주소창 없이 실행합니다.
    # --app 옵션을 주면 해선님이 원하시는 대로 주소창, 메뉴가 사라집니다.
    edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
    
    if os.path.exists(edge_path):
        subprocess.Popen([edge_path, f"--app={URL}"])
        print(f"🚀 Monewment 게이트웨이가 {URL} 에서 실행되었습니다.")
    else:
        print("❌ Edge 브라우저를 찾을 수 없습니다.")

if __name__ == "__main__":
    launch()
    