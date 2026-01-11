# 보안 및 프로덕션 준비도 개선 계획

## 개요

보안 분석 결과 발견된 15개의 문제점을 3단계로 나누어 해결합니다.

- **Phase 1 (Critical)**: 프로덕션 배포 차단 요소 5개 (1-2일)
- **Phase 2 (High Priority)**: 보안 및 안정성 강화 5개 (1주일)
- **Phase 3 (Medium Priority)**: 운영 품질 개선 5개 (2주일)

## 사용자 검토 필요 사항

> [!WARNING]
> **Breaking Changes**
> 
> 1. **환경 변수 추가 필수**: `ANT_ENCRYPTION_KEY`, `ALLOWED_ORIGINS`, `DEBUG` 등 새로운 환경 변수가 필요합니다.
> 2. **기존 .env 파일 업데이트 필요**: 모든 환경에서 `.env` 파일을 새로운 형식으로 업데이트해야 합니다.
> 3. **Docker Compose 재빌드 필요**: 환경 변수 변경으로 인해 컨테이너 재생성이 필요합니다.

> [!IMPORTANT]
> **보안 키 생성 필요**
> 
> 배포 전에 다음 키들을 안전하게 생성하고 관리해야 합니다:
> - `SECRET_KEY` (32자 이상)
> - `ANT_ENCRYPTION_KEY` (64자 hex)
> - `POSTGRES_PASSWORD` (강력한 비밀번호)

## 제안된 변경 사항

### Phase 1: Critical Issues (즉시 수정)

---

#### [MODIFY] [main.py](file:///d:/projects/Monewment/src/main.py)

**변경 내용:**
1. **CORS 설정 수정** (L202-208)
   - `allow_origins=["*"]` → 환경 변수에서 로드
   - 허용 메서드/헤더 명시적 지정

2. **DEBUG print 문 제거** (L199, L429, L436, L439, L442, L660, L664, L673, L684, L692, L700)
   - 모든 `print()` → `logger.debug()` 변경
   - 민감 정보 로깅 제거

3. **DB 연결 실패 처리** (L158-163)
   - 예외 발생 시 `raise RuntimeError()` 추가
   - 재시도 로직 구현

4. **중복 코드 제거** (L20-22, L31-38)
   - 중복 import 제거
   - 중복 변수 선언 제거

---

#### [MODIFY] [config.py](file:///d:/projects/Monewment/src/config.py)

**변경 내용:**
1. **새로운 환경 변수 추가**
   ```python
   DEBUG: bool = False
   ALLOWED_ORIGINS: str = "http://localhost:3000"
   ANT_ENCRYPTION_KEY: str  # 필수
   LOG_LEVEL: str = "INFO"
   ```

2. **환경 변수 검증 추가**
   ```python
   @field_validator('SECRET_KEY')
   def validate_secret_key(cls, v):
       if len(v) < 32:
           raise ValueError("SECRET_KEY must be at least 32 characters")
       return v
   ```

---

#### [MODIFY] [ant_security.py](file:///d:/projects/Monewment/src/core/ant_security.py)

**변경 내용:**
1. **하드코딩된 키 제거** (L20)
   - 환경 변수에서 키 로드
   - 키 없을 시 명확한 에러 메시지

```python
def __init__(self, key_bytes: bytes = None):
    if key_bytes:
        if len(key_bytes) != 32:
            raise ValueError("AES-256 requires a 32-byte key.")
        self.aesgcm = AESGCM(key_bytes)
    else:
        # Load from environment
        key_hex = os.getenv("ANT_ENCRYPTION_KEY")
        if not key_hex:
            raise RuntimeError(
                "ANT_ENCRYPTION_KEY environment variable not set. "
                "Generate one with: python -c 'import secrets; print(secrets.token_hex(32))'"
            )
        self.aesgcm = AESGCM(bytes.fromhex(key_hex))
```

---

#### [MODIFY] [redis_client.py](file:///d:/projects/Monewment/src/core/redis_client.py)

**변경 내용:**
1. **get_client 반환 타입 변경** (L33-36)
   - `Optional[redis.Redis]` 반환
   - 재연결 시도 로직 추가

2. **연결 실패 시 None 반환**
   ```python
   def get_client(self) -> Optional[redis.Redis]:
       if not self.redis:
           logger.warning("Redis not connected")
           return None
       return self.redis
   ```

---

#### [MODIFY] [docker-compose.yml](file:///d:/projects/Monewment/docker-compose.yml)

**변경 내용:**
1. **하드코딩된 비밀번호 제거** (L10-11)
   ```yaml
   environment:
     POSTGRES_USER: ${POSTGRES_USER:-user}
     POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
     POSTGRES_DB: ${POSTGRES_DB:-monewment}
   ```

---

#### [NEW] [.env.example](file:///d:/projects/Monewment/.env.example)

**새 파일 생성:**
```env
# Application
PROJECT_NAME=Monewment
DEBUG=false
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Security
SECRET_KEY=your-secret-key-at-least-32-characters-long
ANT_ENCRYPTION_KEY=generate-with-python-secrets-token-hex-32

# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=user
POSTGRES_PASSWORD=your-strong-password
POSTGRES_DB=monewment
POSTGRES_PORT=5433

# Redis
REDIS_URL=redis://localhost:6379/0

# AI APIs
GEMINI_API_KEY=your-gemini-api-key
CLAUDE_API_KEY=your-claude-api-key

# Blender
BLENDER_PATH=C:\\Program Files\\Blender Foundation\\Blender 5.0\\blender.exe
```

---

#### [NEW] [scripts/generate_keys.py](file:///d:/projects/Monewment/scripts/generate_keys.py)

**새 파일 생성:**
보안 키 생성 스크립트
```python
#!/usr/bin/env python3
import secrets

print("=== Monewment Security Keys Generator ===\n")
print(f"SECRET_KEY={secrets.token_urlsafe(32)}")
print(f"ANT_ENCRYPTION_KEY={secrets.token_hex(32)}")
print(f"POSTGRES_PASSWORD={secrets.token_urlsafe(16)}")
print("\nCopy these to your .env file")
```

---

### Phase 2: High Priority Issues

---

#### [MODIFY] [main.py](file:///d:/projects/Monewment/src/main.py)

**추가 변경 내용:**

1. **WebSocket 실패 카운터 추가** (L632-740)
   ```python
   failed_attempts = 0
   MAX_FAILED_ATTEMPTS = 3
   
   # 복호화 실패 시
   failed_attempts += 1
   if failed_attempts >= MAX_FAILED_ATTEMPTS:
       await websocket.close(code=4003)
       return
   ```

2. **Health Check 엔드포인트 추가**
   ```python
   @app.get("/health")
   async def health_check(db: AsyncSession = Depends(get_db)):
       checks = {
           "database": False,
           "redis": False,
       }
       
       try:
           await db.execute(select(1))
           checks["database"] = True
       except:
           pass
       
       try:
           redis = RedisManager.get_instance().get_client()
           if redis:
               await redis.ping()
               checks["redis"] = True
       except:
           pass
       
       if all(checks.values()):
           return {"status": "healthy", "checks": checks}
       else:
           raise HTTPException(status_code=503, detail=checks)
   ```

---

#### [MODIFY] [requirements.txt](file:///d:/projects/Monewment/requirements.txt)

**추가 의존성:**
```txt
# Rate Limiting
slowapi

# Environment validation
python-dotenv
```

---

### Phase 3: Medium Priority Issues

---

#### [NEW] [schemas.py 확장](file:///d:/projects/Monewment/src/schemas.py)

**API 응답 표준화:**
```python
from pydantic import BaseModel
from typing import Optional, Dict, Any

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class HealthCheckResponse(BaseModel):
    status: str
    checks: Dict[str, bool]
```

---

## 검증 계획

### 자동화된 테스트

#### 1. 환경 변수 검증 테스트
```bash
# 위치: tests/test_config.py
pytest tests/test_config.py -v
```

**테스트 내용:**
- SECRET_KEY 길이 검증
- 필수 환경 변수 존재 확인
- ALLOWED_ORIGINS 파싱 테스트

#### 2. 보안 테스트
```bash
# 위치: tests/test_security.py
pytest tests/test_security.py -v
```

**테스트 내용:**
- 암호화 키 환경 변수 로드
- CORS 설정 검증
- WebSocket 실패 카운터 동작

#### 3. 데이터베이스 연결 테스트
```bash
# 위치: tests/test_database.py
pytest tests/test_database.py -v
```

**테스트 내용:**
- DB 연결 실패 시 앱 시작 중단
- Redis 연결 실패 시 None 반환

### 수동 검증

#### 1. Docker 환경 테스트
```bash
# 1. 환경 변수 설정
cp .env.example .env
python scripts/generate_keys.py >> .env
# .env 파일 편집하여 키 추가

# 2. Docker Compose 재빌드
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d

# 3. Health Check 확인
curl http://localhost:8000/health

# 4. 로그 확인 (DEBUG print 없어야 함)
docker-compose logs backend | grep "DEBUG:"
```

**예상 결과:**
- Health check 응답: `{"status": "healthy", "checks": {"database": true, "redis": true}}`
- DEBUG print 문 없음
- 모든 서비스 정상 시작

#### 2. CORS 테스트
```bash
# 허용되지 않은 도메인에서 요청 (실패해야 함)
curl -H "Origin: http://malicious.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS http://localhost:8000/api/auth/login

# 허용된 도메인에서 요청 (성공해야 함)
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS http://localhost:8000/api/auth/login
```

**예상 결과:**
- 첫 번째 요청: CORS 에러
- 두 번째 요청: 200 OK

#### 3. WebSocket 보안 테스트
```bash
# Python 스크립트로 WebSocket 연결 및 잘못된 데이터 전송
python tests/manual/test_websocket_security.py
```

**예상 결과:**
- 3회 실패 후 연결 종료
- 로그에 보안 경고 출력

### 성능 테스트

#### 부하 테스트
```bash
# Locust 또는 Apache Bench 사용
ab -n 1000 -c 10 http://localhost:8000/health
```

**예상 결과:**
- 평균 응답 시간 < 200ms
- 에러율 0%

---

## 배포 체크리스트

### 배포 전
- [ ] `.env.example` 파일 생성 완료
- [ ] 보안 키 생성 및 `.env` 설정
- [ ] 모든 테스트 통과 확인
- [ ] Docker 환경에서 정상 작동 확인
- [ ] CORS 설정 프로덕션 도메인으로 변경
- [ ] DEBUG 모드 비활성화 확인

### 배포 후
- [ ] Health Check 엔드포인트 모니터링 설정
- [ ] 로그 레벨 INFO로 설정
- [ ] 에러 추적 시스템 연동 (Sentry 등)
- [ ] 보안 스캔 실행

---

## 예상 소요 시간

| Phase | 작업 | 소요 시간 |
|-------|------|-----------|
| Phase 1 | Critical Issues 수정 | 4-6시간 |
| Phase 1 | 테스트 작성 및 검증 | 2-3시간 |
| Phase 2 | High Priority 수정 | 4-5시간 |
| Phase 2 | 테스트 및 검증 | 2-3시간 |
| Phase 3 | Medium Priority 수정 | 6-8시간 |
| Phase 3 | 통합 테스트 | 3-4시간 |
| **총계** | | **21-29시간** |

---

## 위험 요소 및 대응 방안

### 위험 1: 기존 클라이언트 호환성
**문제:** 암호화 키 변경 시 기존 연결된 클라이언트 작동 중단

**대응:**
- 클라이언트 업데이트 공지
- 점진적 마이그레이션 (구 키와 신 키 동시 지원)

### 위험 2: 환경 변수 누락
**문제:** 배포 시 필수 환경 변수 누락으로 앱 시작 실패

**대응:**
- 시작 시 환경 변수 검증 로직 추가
- 명확한 에러 메시지 제공
- `.env.example` 문서화

### 위험 3: CORS 설정 오류
**문제:** 프론트엔드 연결 차단

**대응:**
- 스테이징 환경에서 충분한 테스트
- 롤백 계획 수립
