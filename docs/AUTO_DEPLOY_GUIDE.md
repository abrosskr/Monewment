# Monewment 자동 배포 시스템 사용 가이드

> **버전:** Phase 1 완료  
> **상태:** Kubernetes 연동 완료

---

## 🚀 빠른 시작

### 1. 사전 준비

#### Kubernetes 클러스터
```bash
# Minikube (로컬 테스트용)
minikube start

# 또는 실제 클러스터 kubeconfig 설정
export KUBECONFIG=~/.kube/config
```

#### Docker 레지스트리
```bash
# 로컬 레지스트리 실행
docker run -d -p 5000:5000 --name registry registry:2

# 또는 Docker Hub 사용
docker login
```

#### Ingress Controller
```bash
# NGINX Ingress Controller 설치
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
```

#### cert-manager (SSL 자동 발급)
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

---

## 📦 자동 배포 사용법

### 기본 배포
```bash
curl -X POST http://localhost:8000/api/v1/deploy/auto-deploy \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "git_repo": "https://github.com/username/my-app",
    "git_branch": "main",
    "port": 8080
  }'
```

### 환경 변수 포함 배포
```bash
curl -X POST http://localhost:8000/api/v1/deploy/auto-deploy \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "git_repo": "https://github.com/username/my-app",
    "port": 3000,
    "env_vars": {
      "DATABASE_URL": "postgres://user:pass@host:5432/db",
      "API_KEY": "secret_key_12345",
      "NODE_ENV": "production"
    }
  }'
```

### Private 저장소 배포
```bash
curl -X POST http://localhost:8000/api/v1/deploy/auto-deploy \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "git_repo": "https://github.com/username/private-app",
    "git_token": "ghp_your_github_token",
    "port": 8080
  }'
```

---

## 📊 배포 상태 확인

### 배포 상태 조회
```bash
curl http://localhost:8000/api/v1/deploy/deployments/1
```

**응답 예시:**
```json
{
  "id": 1,
  "project_id": 1,
  "git_repo": "https://github.com/username/my-app",
  "git_branch": "main",
  "status": "DEPLOYED",
  "url": "https://my-app.monewment.io",
  "last_deployed_at": "2026-01-11T12:00:00Z"
}
```

### 빌드 로그 확인
```bash
curl http://localhost:8000/api/v1/deploy/deployments/1/logs
```

---

## 🔧 Dockerfile 요구사항

### 기본 Dockerfile 예시
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

### Python 앱 예시
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "app.py"]
```

---

## 🌐 도메인 및 SSL

### 자동 할당되는 도메인
- 패턴: `{project-name}.monewment.io`
- SSL: 자동 발급 (Let's Encrypt)
- 예시: `https://my-app.monewment.io`

### DNS 설정 (필요시)
```bash
# *.monewment.io를 Ingress Controller IP로 설정
# A 레코드: *.monewment.io -> <INGRESS_IP>

# Ingress IP 확인
kubectl get svc -n ingress-nginx
```

---

## 🐛 문제 해결

### 배포 실패 시
```bash
# 1. 빌드 로그 확인
curl http://localhost:8000/api/v1/deploy/deployments/1/logs

# 2. Kubernetes 리소스 확인
kubectl get deployments -n monewment
kubectl get pods -n monewment
kubectl logs <pod-name> -n monewment

# 3. Ingress 확인
kubectl get ingress -n monewment
kubectl describe ingress <ingress-name> -n monewment
```

### Docker 빌드 실패
```bash
# Dockerfile 위치 확인
# 저장소 루트에 Dockerfile이 있어야 함

# 수동 빌드 테스트
git clone <your-repo>
cd <your-repo>
docker build -t test .
```

---

## 📋 체크리스트

### 배포 전
- [ ] Kubernetes 클러스터 실행 중
- [ ] Docker 레지스트리 설정 완료
- [ ] Ingress Controller 설치
- [ ] cert-manager 설치 (SSL용)
- [ ] 저장소에 Dockerfile 존재

### 배포 후
- [ ] 배포 상태 확인 (DEPLOYED)
- [ ] Pod 실행 확인
- [ ] 도메인 접속 확인
- [ ] SSL 인증서 확인

---

## 🎯 다음 단계

- Webhook 설정 (Git push 시 자동 배포)
- 롤백 기능
- Blue-Green 배포
- Canary 배포
- 오토스케일링
