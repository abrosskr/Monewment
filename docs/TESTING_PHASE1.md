# Phase 1 완료 후 테스트 가이드

## 1. 환경 변수 생성

```bash
# 1. 보안 키 생성
python scripts/generate_keys.py

# 2. .env 파일 생성 (아직 없다면)
cp .env.example .env

# 3. 생성된 키를 .env 파일에 복사
# 에디터로 .env 파일을 열고 다음 값들을 업데이트:
# - SECRET_KEY
# - ANT_ENCRYPTION_KEY  
# - POSTGRES_PASSWORD
```

## 2. 로컬 환경 테스트

```bash
# 1. 의존성 설치 확인
pip install -r requirements.txt

# 2. 애플리케이션 시작
uvicorn src.main:app --reload

# 예상 결과:
# ✅ Database Tables Verified (Async Mode).
# ✅ System Collector Attached.
# ✅ Redis Connected.
# INFO:     Application startup complete.
```

## 3. Docker 환경 테스트

```bash
# 1. 기존 컨테이너 정리
docker-compose down -v

# 2. 재빌드 및 시작
docker-compose build --no-cache
docker-compose up -d

# 3. 로그 확인
docker-compose logs backend

# 4. Health Check (Phase 2에서 추가 예정)
curl http://localhost:8000/
```

## 4. CORS 테스트

```bash
# 허용되지 않은 도메인 (실패해야 함)
curl -H "Origin: http://malicious.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS http://localhost:8000/api/auth/login

# 허용된 도메인 (성공해야 함)
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS http://localhost:8000/api/auth/login
```

## 5. 에러 처리 테스트

### DB 연결 실패 테스트
```bash
# PostgreSQL 중지
docker-compose stop db

# 애플리케이션 시작 시도 (실패해야 함)
uvicorn src.main:app

# 예상 결과:
# ❌ DB Init Error: ...
# RuntimeError: Database initialization failed. Cannot start application.
```

### Redis 연결 실패 테스트
```bash
# Redis 중지
docker-compose stop redis

# 애플리케이션 시작 (경고와 함께 시작되어야 함)
uvicorn src.main:app

# 예상 결과:
# WARNING: Redis not connected. Some features may be unavailable.
# INFO: Application startup complete.
```

## 6. 검증 체크리스트

- [ ] 애플리케이션이 정상적으로 시작됨
- [ ] CORS 설정이 환경 변수 기반으로 작동함
- [ ] DB 연결 실패 시 앱이 시작되지 않음
- [ ] Redis 연결 실패 시 경고와 함께 앱이 시작됨
- [ ] 암호화 키가 환경 변수에서 로드됨
- [ ] Docker 환경에서 정상 작동함
- [ ] DEBUG print 문이 제거됨

## 다음 단계

Phase 1이 완료되면 Phase 2 (High Priority Issues)로 진행:
- WebSocket 실패 카운터
- Rate Limiting
- Health Check 엔드포인트
- API 응답 표준화
