# Monewment 배포 가이드

> **버전:** v4.8-UIFactory (Security Hardened)  
> **최종 업데이트:** 2026-01-11

---

## 📋 사전 요구사항

### 시스템 요구사항
- **OS:** Linux (Ubuntu 20.04+), Windows Server 2019+, macOS 11+
- **Python:** 3.10 이상
- **Node.js:** 18.x 이상 (프론트엔드)
- **Docker:** 20.10+ (선택사항)
- **PostgreSQL:** 15+
- **Redis:** 7+

### 필수 도구
```bash
# Python 패키지 관리자
pip install --upgrade pip

# Docker (선택)
docker --version
docker-compose --version
```

---

## 🔐 1단계: 보안 키 생성

```bash
# 프로젝트 디렉토리로 이동
cd d:\projects\Monewment

# 보안 키 생성
python scripts/generate_keys.py

# 출력 예시:
# SECRET_KEY=...
# ANT_ENCRYPTION_KEY=...
# POSTGRES_PASSWORD=...
```

---

## ⚙️ 2단계: 환경 변수 설정

### .env 파일 생성
```bash
# .env.example을 복사
cp .env.example .env

# 에디터로 .env 파일 열기
notepad .env  # Windows
nano .env     # Linux/Mac
```

### 필수 환경 변수 설정
```env
# Application
PROJECT_NAME=Monewment
DEBUG=false
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Security (1단계에서 생성한 키 사용)
SECRET_KEY=<생성된 키>
ANT_ENCRYPTION_KEY=<생성된 키>

# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=user
POSTGRES_PASSWORD=<생성된 비밀번호>
POSTGRES_DB=monewment
POSTGRES_PORT=5433

# Redis
REDIS_URL=redis://localhost:6379/0

# AI APIs
GEMINI_API_KEY=<your-api-key>
```

---

## 🐳 3단계: Docker 배포 (권장)

### Docker Compose로 전체 스택 실행
```bash
# 컨테이너 빌드 및 시작
docker-compose up -d --build

# 로그 확인
docker-compose logs -f backend

# Health Check
curl http://localhost:8000/health
```

### 개별 서비스 관리
```bash
# 서비스 중지
docker-compose stop

# 서비스 재시작
docker-compose restart backend

# 볼륨 포함 완전 삭제
docker-compose down -v
```

---

## 💻 4단계: 로컬 배포 (개발 환경)

### 의존성 설치
```bash
# 백엔드 의존성
pip install -r requirements.txt

# 프론트엔드 의존성
cd gui
npm install
```

### 데이터베이스 설정
```bash
# PostgreSQL 시작 (Docker)
docker run -d \
  --name monewment-db \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=<your-password> \
  -e POSTGRES_DB=monewment \
  -p 5433:5432 \
  postgres:15-alpine

# Redis 시작 (Docker)
docker run -d \
  --name monewment-redis \
  -p 6379:6379 \
  redis:7-alpine
```

### 애플리케이션 시작
```bash
# 백엔드 (터미널 1)
uvicorn src.main:app --host 0.0.0.0 --port 8000

# 프론트엔드 (터미널 2)
cd gui
npm run dev
```

---

## ☸️ 5단계: Kubernetes 배포 (프로덕션)

### ConfigMap 생성
```bash
kubectl create configmap monewment-config \
  --from-env-file=.env
```

### Secret 생성
```bash
kubectl create secret generic monewment-secrets \
  --from-literal=SECRET_KEY=<your-key> \
  --from-literal=ANT_ENCRYPTION_KEY=<your-key> \
  --from-literal=POSTGRES_PASSWORD=<your-password>
```

### 배포
```bash
# Namespace 생성
kubectl create namespace monewment

# 배포 적용
kubectl apply -f k8s/ -n monewment

# 상태 확인
kubectl get pods -n monewment
kubectl get svc -n monewment
```

---

## 🧪 6단계: 배포 검증

### Health Check
```bash
curl http://localhost:8000/health

# 예상 응답:
{
  "status": "healthy",
  "checks": {
    "database": true,
    "redis": true
  }
}
```

### API 테스트
```bash
# 회원가입
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123","name":"Test User"}'

# 로그인
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'
```

### Rate Limiting 확인
```bash
# 5회 이상 로그인 시도
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"wrong"}' \
    -w "\nStatus: %{http_code}\n"
done

# 6번째 요청에서 429 에러 예상
```

---

## 📊 7단계: 모니터링 설정

### 로그 확인
```bash
# Docker
docker-compose logs -f backend

# Kubernetes
kubectl logs -f deployment/monewment-backend -n monewment
```

### Health Check 모니터링
```bash
# Cron으로 주기적 체크 (Linux)
*/5 * * * * curl -f http://localhost:8000/health || echo "Health check failed" | mail -s "Monewment Alert" admin@yourdomain.com
```

---

## 🔧 문제 해결

### 데이터베이스 연결 실패
```bash
# 에러: Database initialization failed
# 해결:
1. PostgreSQL이 실행 중인지 확인
2. .env의 POSTGRES_* 변수 확인
3. 포트 충돌 확인 (5433)
```

### Redis 연결 실패
```bash
# 경고: Redis not connected
# 해결:
1. Redis가 실행 중인지 확인
2. REDIS_URL 확인
3. 방화벽 설정 확인 (6379 포트)
```

### Rate Limit 에러
```bash
# 에러: 429 Too Many Requests
# 해결:
1. 정상 동작 (보안 기능)
2. 1분 대기 후 재시도
3. 필요시 limits 조정 (main.py)
```

---

## 🚀 성능 최적화

### 프로덕션 설정
```env
# .env
DEBUG=false
LOG_LEVEL=WARNING
WORKERS=4  # CPU 코어 수
```

### Uvicorn 워커 설정
```bash
uvicorn src.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level warning
```

---

## 📚 추가 문서

- [보안 분석 보고서](file:///d:/projects/Monewment/docs/security_analysis.md)
- [Phase 1 완료 보고서](file:///d:/projects/Monewment/docs/PHASE1_COMPLETION.md)
- [Phase 2 완료 보고서](file:///d:/projects/Monewment/docs/PHASE2_COMPLETION.md)
- [API 문서](http://localhost:8000/docs) - FastAPI Swagger UI
