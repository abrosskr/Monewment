# Monewment 로깅 시스템 현황 분석 보고서

> **분석 일자:** 2026-01-11  
> **분석 범위:** 로그 생성, 저장, 분석 시스템  
> **종합 평가:** 🟡 **기본 구현 완료, 프로덕션 수준 개선 필요**

---

## 📊 현재 구현 상태 요약

| 영역 | 구현 상태 | 수준 | 평가 |
|------|-----------|------|------|
| **로그 생성** | ✅ 구현됨 | B+ | 양호 |
| **로그 저장** | 🟡 부분 구현 | C | 개선 필요 |
| **로그 분석** | ❌ 미구현 | F | 구현 필요 |
| **로그 수집** | ❌ 미구현 | F | 구현 필요 |
| **모니터링** | 🟡 부분 구현 | C+ | 개선 필요 |

---

## 1️⃣ 로그 생성 (Log Generation)

### ✅ 구현된 기능

#### 1.1 Structlog 기반 구조화 로깅
**파일:** [`src/core/logger.py`](file:///d:/projects/Monewment/src/core/logger.py)

```python
# 현재 구현
- structlog 사용 (JSON 형식)
- ISO 타임스탬프
- 로그 레벨 자동 추가
- 스택 정보 렌더링
- 환경 변수 기반 LOG_LEVEL 설정
```

**장점:**
- ✅ 구조화된 JSON 로그 (기계 파싱 가능)
- ✅ 환경별 로그 레벨 조정 가능
- ✅ 타임스탬프 표준화 (ISO 8601)

#### 1.2 로그 사용 현황
**분석 결과:**
- `logger.info`: 60+ 곳에서 사용
- `logger.error`: 40+ 곳에서 사용
- `logger.warning`: 10+ 곳에서 사용

**주요 로깅 영역:**
1. 애플리케이션 시작/종료
2. WebSocket 연결/해제
3. 작업 디스패치 및 완료
4. 에러 및 예외 처리
5. Health Check 실패

### 🟡 부족한 부분

#### 1.3 로그 컨텍스트 부족
```python
# 현재
logger.info("Job completed")

# 권장 (컨텍스트 추가)
logger.info("job_completed", 
    job_id=job.id, 
    worker_id=worker.id, 
    duration_ms=elapsed_time,
    status="success"
)
```

#### 1.4 민감 정보 필터링 미흡
```python
# 위험: 비밀번호, 토큰 등이 로그에 노출될 수 있음
logger.error(f"Login failed for {email}")  # OK
logger.debug(f"Token: {access_token}")     # ❌ 위험
```

#### 1.5 요청 추적 ID 부재
- 분산 시스템에서 요청 추적 불가
- 여러 서비스 간 로그 연결 어려움

---

## 2️⃣ 로그 저장 (Log Storage)

### 🟡 현재 상태

#### 2.1 표준 출력 (stdout)
```python
# logger.py
logging.basicConfig(
    stream=sys.stdout,  # 콘솔 출력만
    level=log_level,
)
```

**문제점:**
- ❌ 로그가 영구 저장되지 않음
- ❌ 애플리케이션 재시작 시 로그 손실
- ❌ 로그 검색 불가능

#### 2.2 프로젝트별 로그 파일
**위치:** `projects/{project_name}/main.log`

```python
# main.py에서 생성
with open(os.path.join(target_path, "main.log"), "w") as f:
    f.write(f"[{datetime.now()}] Project '{req.project_name}' initialized...")
```

**문제점:**
- ❌ 단순 텍스트 파일 (구조화 안 됨)
- ❌ 로테이션 없음 (무한 증가)
- ❌ 애플리케이션 로그와 분리됨

### ❌ 미구현 기능

1. **로그 파일 로테이션**
   - 파일 크기 제한 없음
   - 오래된 로그 자동 삭제 없음

2. **중앙 집중식 로그 저장소**
   - Elasticsearch, Loki 등 미연동
   - 로그 검색 불가능

3. **로그 백업**
   - 로그 손실 위험

---

## 3️⃣ 로그 수집 (Log Collection)

### ❌ 완전 미구현

#### 3.1 필요한 기능
1. **로그 수집 에이전트**
   - Fluentd, Filebeat, Vector 등
   - 여러 소스에서 로그 수집

2. **로그 파이프라인**
   - 로그 필터링
   - 로그 변환
   - 로그 라우팅

3. **분산 추적**
   - OpenTelemetry
   - Jaeger, Zipkin

#### 3.2 현재 상황
- ❌ 로그 수집 에이전트 없음
- ❌ 로그 파이프라인 없음
- ❌ 분산 추적 시스템 없음

---

## 4️⃣ 로그 분석 (Log Analysis)

### ❌ 완전 미구현

#### 4.1 필요한 기능
1. **로그 검색**
   - 키워드 검색
   - 시간 범위 필터링
   - 정규식 검색

2. **로그 시각화**
   - 대시보드
   - 그래프 및 차트
   - 실시간 모니터링

3. **로그 분석**
   - 에러율 계산
   - 성능 메트릭 추출
   - 이상 탐지

4. **알림**
   - 에러 임계값 초과 시 알림
   - Slack, Email 통합

#### 4.2 현재 상황
- ❌ 로그 검색 기능 없음
- ❌ 로그 시각화 없음
- ❌ 로그 분석 도구 없음
- ❌ 알림 시스템 없음

---

## 5️⃣ 모니터링 (Monitoring)

### 🟡 부분 구현

#### 5.1 구현된 기능
- ✅ Health Check 엔드포인트 (`/health`)
- ✅ DB/Redis 연결 상태 체크

#### 5.2 미구현 기능
- ❌ Prometheus 메트릭 노출
- ❌ 커스텀 메트릭 (요청 수, 응답 시간 등)
- ❌ Grafana 대시보드
- ❌ APM (Application Performance Monitoring)

---

## 📋 개선 권장 사항

### 우선순위 1 (즉시 필요)

#### 1. 로그 파일 로테이션 구현
```python
# logger.py 개선
from logging.handlers import RotatingFileHandler

file_handler = RotatingFileHandler(
    'logs/monewment.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

#### 2. 민감 정보 필터링
```python
# 민감 정보 마스킹 프로세서 추가
def mask_sensitive_data(logger, method_name, event_dict):
    sensitive_keys = ['password', 'token', 'api_key', 'secret']
    for key in sensitive_keys:
        if key in event_dict:
            event_dict[key] = '***MASKED***'
    return event_dict

processors.insert(0, mask_sensitive_data)
```

#### 3. 요청 추적 ID 추가
```python
# middleware 추가
import uuid
from fastapi import Request

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # 로그에 request_id 자동 추가
    structlog.contextvars.bind_contextvars(request_id=request_id)
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

### 우선순위 2 (단기)

#### 4. ELK Stack 또는 Loki 연동
```yaml
# docker-compose.yml에 추가
services:
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
  
  promtail:
    image: grafana/promtail:latest
    volumes:
      - ./logs:/var/log
      - ./promtail-config.yml:/etc/promtail/config.yml
```

#### 5. Prometheus 메트릭 추가
```python
# requirements.txt
prometheus-fastapi-instrumentator

# main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### 우선순위 3 (중기)

#### 6. 로그 분석 대시보드
- Grafana 설정
- 주요 메트릭 시각화
- 알림 규칙 설정

#### 7. 분산 추적 시스템
- OpenTelemetry 통합
- Jaeger 또는 Zipkin 설정

---

## 🎯 구현 로드맵

### Phase 1: 기본 개선 (1주일)
- [ ] 로그 파일 로테이션
- [ ] 민감 정보 필터링
- [ ] 요청 추적 ID
- [ ] 로그 레벨별 파일 분리

### Phase 2: 로그 수집 (2주일)
- [ ] Loki + Promtail 설정
- [ ] 로그 파이프라인 구축
- [ ] 로그 검색 기능

### Phase 3: 모니터링 (2주일)
- [ ] Prometheus 메트릭
- [ ] Grafana 대시보드
- [ ] 알림 시스템

### Phase 4: 고급 기능 (1개월)
- [ ] 분산 추적
- [ ] 로그 분석 자동화
- [ ] 이상 탐지

---

## 📊 비교: 현재 vs 이상적 상태

| 기능 | 현재 | 이상적 상태 |
|------|------|-------------|
| 로그 형식 | ✅ JSON | ✅ JSON |
| 로그 레벨 | ✅ 환경 변수 | ✅ 환경 변수 |
| 로그 저장 | 🟡 stdout만 | ✅ 파일 + 중앙 저장소 |
| 로그 로테이션 | ❌ 없음 | ✅ 자동 로테이션 |
| 로그 검색 | ❌ 불가능 | ✅ 전문 검색 |
| 로그 시각화 | ❌ 없음 | ✅ Grafana 대시보드 |
| 요청 추적 | ❌ 없음 | ✅ 분산 추적 |
| 알림 | ❌ 없음 | ✅ Slack/Email |
| 메트릭 | 🟡 Health Check만 | ✅ Prometheus |

---

## 💡 즉시 적용 가능한 개선 코드

### 1. 로그 파일 핸들러 추가
```python
# src/core/logger.py
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

def setup_logger():
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # 로그 디렉토리 생성
    log_dir = settings.BASE_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # 파일 핸들러 추가
    file_handler = RotatingFileHandler(
        log_dir / "monewment.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    
    # 에러 전용 파일
    error_handler = RotatingFileHandler(
        log_dir / "errors.log",
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    
    logging.basicConfig(
        format="%(message)s",
        level=log_level,
        handlers=[
            logging.StreamHandler(sys.stdout),
            file_handler,
            error_handler
        ]
    )
```

### 2. 요청 ID 미들웨어
```python
# src/middleware/request_id.py
import uuid
from fastapi import Request
import structlog

async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    
    # 컨텍스트에 request_id 바인딩
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        path=request.url.path,
        method=request.method
    )
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    # 컨텍스트 정리
    structlog.contextvars.clear_contextvars()
    
    return response
```

---

## 🎓 결론

### 현재 수준
- **로그 생성:** B+ (구조화 로깅 구현, 컨텍스트 부족)
- **로그 저장:** C (stdout만, 영구 저장 없음)
- **로그 분석:** F (완전 미구현)
- **종합:** **C+ (기본 기능만 구현, 프로덕션 부적합)**

### 프로덕션 배포를 위한 최소 요구사항
1. ✅ 로그 파일 로테이션
2. ✅ 민감 정보 필터링
3. ✅ 요청 추적 ID
4. ✅ 중앙 로그 저장소 (Loki/ELK)
5. ✅ 기본 모니터링 대시보드

**권장:** Phase 1-2 완료 후 프로덕션 배포
