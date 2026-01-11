# 로깅 시스템 사용 가이드

> **버전:** v5.0 (Advanced Logging)  
> **최종 업데이트:** 2026-01-11

---

## 📋 개요

Monewment 플랫폼은 프로덕션급 로깅 시스템을 갖추고 있습니다:
- ✅ 구조화된 JSON 로깅 (structlog)
- ✅ 자동 로그 파일 로테이션
- ✅ 민감 정보 자동 마스킹
- ✅ 분산 추적 (Request ID)
- ✅ Prometheus 메트릭

---

## 📂 로그 파일 구조

```
logs/
├── monewment.log       # 모든 로그 (INFO 이상)
├── monewment.log.1     # 백업 1
├── monewment.log.2     # 백업 2
├── ...
├── errors.log          # 에러 전용 (ERROR 이상)
├── errors.log.1
├── access.log          # 액세스 로그 (INFO 이상)
└── access.log.1
```

**로테이션 설정:**
- 최대 파일 크기: 10MB
- 백업 개수: 5개 (errors/monewment), 3개 (access)
- 인코딩: UTF-8

---

## 🔧 환경 변수 설정

### LOG_LEVEL 설정
```env
# .env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

**레벨별 용도:**
- `DEBUG`: 개발 환경, 상세한 디버깅 정보
- `INFO`: 프로덕션 기본값, 일반 정보
- `WARNING`: 경고 메시지만
- `ERROR`: 에러만
- `CRITICAL`: 치명적 에러만

---

## 📝 로그 사용 예시

### 기본 로깅
```python
from src.core.logger import setup_logger

logger = setup_logger()

# 정보 로그
logger.info("user_login", user_id=123, email="user@example.com")

# 에러 로그
logger.error("database_connection_failed", 
    error=str(e), 
    host="localhost", 
    port=5432
)

# 경고 로그
logger.warning("rate_limit_approaching", 
    user_id=456, 
    current_requests=45, 
    limit=50
)
```

### 컨텍스트 바인딩
```python
import structlog

# 요청 전체에 걸쳐 컨텍스트 유지
structlog.contextvars.bind_contextvars(
    user_id=user.id,
    organization_id=org.id
)

# 이후 모든 로그에 자동 포함
logger.info("action_performed")  # user_id, organization_id 자동 포함

# 컨텍스트 정리
structlog.contextvars.clear_contextvars()
```

---

## 🔒 민감 정보 보호

### 자동 마스킹되는 키
다음 키워드가 포함된 필드는 자동으로 `***MASKED***`로 변환됩니다:
- `password`
- `token`
- `api_key`
- `secret`
- `authorization`
- `access_token`
- `refresh_token`
- `private_key`
- `hashed_password`

### JWT 토큰 자동 감지
`eyJ`로 시작하는 20자 이상의 문자열은 자동으로 마스킹됩니다:
```python
logger.debug("token_received", token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
# 출력: {"token": "eyJhbGciOi...***MASKED***"}
```

---

## 🔍 요청 추적 (Request ID)

### 자동 생성
모든 HTTP 요청에 고유한 `request_id`가 자동으로 부여됩니다.

### 클라이언트에서 전달
```bash
curl -H "X-Request-ID: my-custom-id-12345" http://localhost:8000/api/...
```

### 로그에서 확인
```json
{
  "event": "request_completed",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "path": "/api/auth/login",
  "method": "POST",
  "status_code": 200,
  "timestamp": "2026-01-11T12:30:00.123456Z"
}
```

### 응답 헤더
모든 응답에 `X-Request-ID` 헤더가 포함됩니다:
```
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
```

---

## 📊 Prometheus 메트릭

### 메트릭 엔드포인트
```bash
curl http://localhost:8000/metrics
```

### 자동 수집되는 메트릭
1. **HTTP 요청 수**
   - `http_requests_total{method="GET", path="/api/...", status="200"}`

2. **응답 시간**
   - `http_request_duration_seconds{method="POST", path="/api/..."}`

3. **진행 중인 요청**
   - `http_requests_inprogress{method="GET", path="/api/..."}`

### Grafana 연동
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'monewment'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

---

## 🔎 로그 검색 및 분석

### jq를 사용한 JSON 로그 파싱
```bash
# 에러 로그만 필터링
cat logs/monewment.log | jq 'select(.level=="error")'

# 특정 request_id 추적
cat logs/monewment.log | jq 'select(.request_id=="550e8400-...")'

# 특정 시간 범위
cat logs/monewment.log | jq 'select(.timestamp > "2026-01-11T12:00:00")'

# 에러 통계
cat logs/errors.log | jq -r '.event' | sort | uniq -c | sort -rn
```

### Python으로 로그 분석
```python
import json

with open('logs/monewment.log', 'r') as f:
    for line in f:
        log = json.loads(line)
        if log.get('level') == 'error':
            print(f"{log['timestamp']}: {log['event']}")
```

---

## 🚨 알림 설정 (권장)

### Loki + Promtail 연동
```yaml
# promtail-config.yml
server:
  http_listen_port: 9080

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: monewment
    static_configs:
      - targets:
          - localhost
        labels:
          job: monewment
          __path__: /path/to/logs/*.log
```

### Slack 알림 (Python 스크립트)
```python
# scripts/alert_on_errors.py
import json
import requests
from datetime import datetime, timedelta

SLACK_WEBHOOK = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
ERROR_THRESHOLD = 10  # 10분에 10개 이상 에러 시 알림

# 최근 10분간 에러 카운트
recent_errors = []
with open('logs/errors.log', 'r') as f:
    for line in f:
        log = json.loads(line)
        timestamp = datetime.fromisoformat(log['timestamp'])
        if datetime.now() - timestamp < timedelta(minutes=10):
            recent_errors.append(log)

if len(recent_errors) >= ERROR_THRESHOLD:
    requests.post(SLACK_WEBHOOK, json={
        "text": f"🚨 Alert: {len(recent_errors)} errors in last 10 minutes!"
    })
```

---

## 🧪 테스트

### 로그 생성 테스트
```bash
# 애플리케이션 시작
uvicorn src.main:app --reload

# 로그 파일 확인
ls -lh logs/

# 실시간 로그 모니터링
tail -f logs/monewment.log | jq .
```

### 민감 정보 마스킹 테스트
```python
# 테스트 스크립트
logger.info("test_masking", 
    password="secret123",  # 마스킹되어야 함
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",  # 마스킹되어야 함
    username="john"  # 마스킹 안 됨
)
```

### Request ID 테스트
```bash
# 요청 전송
curl -H "X-Request-ID: test-123" http://localhost:8000/health

# 로그에서 확인
grep "test-123" logs/access.log
```

---

## 📈 모범 사례

### 1. 구조화된 로깅 사용
```python
# ❌ 나쁜 예
logger.info(f"User {user_id} logged in from {ip}")

# ✅ 좋은 예
logger.info("user_login", user_id=user_id, ip_address=ip)
```

### 2. 적절한 로그 레벨 사용
```python
logger.debug("cache_hit", key="user:123")  # 디버깅 정보
logger.info("payment_processed", amount=100)  # 중요 이벤트
logger.warning("api_rate_limit_approaching", remaining=5)  # 경고
logger.error("payment_failed", error=str(e))  # 에러
logger.critical("database_down", host="db.example.com")  # 치명적
```

### 3. 컨텍스트 활용
```python
# 요청 처리 시작
structlog.contextvars.bind_contextvars(
    request_id=request_id,
    user_id=user.id
)

# 여러 단계에서 로깅
logger.info("step_1_completed")
logger.info("step_2_completed")
logger.info("request_completed")

# 모든 로그에 request_id, user_id 자동 포함
```

---

## 🔧 문제 해결

### 로그 파일이 생성되지 않음
```bash
# 권한 확인
ls -ld logs/

# 디렉토리 생성
mkdir -p logs
chmod 755 logs
```

### 로그 파일이 너무 큼
```python
# logger.py에서 maxBytes 조정
maxBytes=5*1024*1024  # 5MB로 줄임
```

### 메트릭 엔드포인트 접근 불가
```bash
# /metrics 엔드포인트 확인
curl http://localhost:8000/metrics

# 방화벽 확인
sudo ufw allow 8000
```

---

## 📚 참고 자료

- [Structlog 문서](https://www.structlog.org/)
- [Prometheus 가이드](https://prometheus.io/docs/introduction/overview/)
- [Grafana 대시보드](https://grafana.com/docs/)
