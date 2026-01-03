import time
import os
from datetime import datetime

# 로그 파일 경로 설정 (상대 경로 사용으로 안전성 확보)
log_file = "main.log"

# 엔진 시작 시점에 구분선을 그어 화면에서 보기 좋게 만듭니다.
start_msg = f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] >>> AI 에이전트 엔진 가동 시작 <<<\n"
with open(log_file, "a", encoding="utf-8") as f:
    f.write(start_msg)

print("--- AI 에이전트 엔진 가동 시작 ---")

# 해선님 원본 로직: 10번 반복 수행
for i in range(1, 11):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{now}] AI 에이전트가 데이터를 분석 중입니다... ({i}/10)\n"

    # 로그 파일에 추가 기록
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_message)

    # 터미널(백엔드 로그)에도 출력
    print(log_message.strip())
    
    # 3초마다 기록 (해선님 설정 유지)
    time.sleep(3) 

# 분석 완료 로그 기록
end_msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 분석 완료 및 엔진 종료.\n"
with open(log_file, "a", encoding="utf-8") as f:
    f.write(end_msg)

print("--- 분석 완료 및 엔진 종료 ---")