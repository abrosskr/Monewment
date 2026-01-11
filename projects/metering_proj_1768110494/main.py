import time
import os
from datetime import datetime

# 로그 파일 경로 설정 (해선님 원본 유지)
log_file = "main.log"

# 엔진 시작 로그 기록
start_msg = f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] >>> AI 에이전트 가동 시작 <<<\n"
with open(log_file, "a", encoding="utf-8") as f:
    f.write(start_msg)

print("--- AI 에이전트 엔진 가동 시작 ---")

# 표준 10단계 분석 로직
for i in range(1, 11):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{now}] AI 에이전트가 데이터를 분석 중입니다... ({i}/10)\n"
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_message)
    print(log_message.strip())
    
    time.sleep(3) 

end_msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 분석 완료 및 엔진 종료.\n"
with open(log_file, "a", encoding="utf-8") as f:
    f.write(end_msg)

print("--- 분석 완료 및 엔진 종료 ---")