# Monewment 자율주행 호스팅 현황 및 개선 방안

> **분석 일자:** 2026-01-11  
> **현재 상태:** 🟡 **기본 인프라 구축 완료, 자동화 기능 미흡**  
> **목표:** 완전 자율주행 클라우드 호스팅 플랫폼

---

## 📊 현재 구현 상태 요약

### ✅ 구현된 기능 (B+)

#### 1. 클러스터 기반 인프라 관리
**파일:** [`src/models.py`](file:///d:/projects/Monewment/src/models.py) (L107-123)

```python
class Cluster(Base):
    """물리적/논리적 리소스 클러스터"""
    name = Column(String, unique=True)
    region = Column(String, default="kr-seoul-1")
    
    # 하드웨어 용량
    cpu_capacity = Column(Integer, default=100)
    ram_capacity_gb = Column(Integer, default=512)
    gpu_capacity = Column(Integer, default=8)
    
    organizations = relationship("Organization")
```

**기능:**
- ✅ 클러스터 생성 및 관리
- ✅ 리소스 용량 추적
- ✅ Organization에 클러스터 할당

#### 2. KubeVirt 기반 VM 프로비저닝
**파일:** [`src/api/v1/endpoints/vm.py`](file:///d:/projects/Monewment/src/api/v1/endpoints/vm.py)

```python
# VM 생성 API
@router.post("")
async def create_vm(req: VMCreateRequest):
    # 1. DB 레코드 생성
    new_vm = VMInstance(name=req.name, flavor_id=req.flavor_id)
    
    # 2. KubeVirt VMI 생성
    vmi_manifest = {
        "apiVersion": "kubevirt.io/v1",
        "kind": "VirtualMachineInstance",
        "metadata": {"name": req.name},
        "spec": {...}
    }
    k8s.custom_api.create_namespaced_custom_object(...)
```

**기능:**
- ✅ VM 생성/삭제 API
- ✅ KubeVirt 통합 (Stub 모드 지원)
- ✅ 하드웨어 Flavor 선택
- ✅ AI 모델 동적 전환
- ✅ 실시간 과금 계산

#### 3. 계층적 리소스 관리
```
Cluster (물리 자원)
  └─ Organization (법인)
      ├─ Quota (CPU, RAM, GPU)
      └─ Projects (프로젝트)
          └─ VMInstances (가상머신)
```

**기능:**
- ✅ Organization별 쿼터 할당
- ✅ 프로젝트별 VM 관리
- ✅ 사용량 추적 (VMUsage)

---

## ❌ 미구현 기능 (자율주행에 필요)

### 1. 자동 서비스 배포 파이프라인 ❌

**현재 상태:**
- VM은 생성되지만 **빈 VM**만 생성됨
- 사용자가 수동으로 SSH 접속하여 서비스 설치 필요

**필요한 기능:**
```python
# 목표: 코드 → 자동 배포
@router.post("/deploy")
async def auto_deploy_service(
    project_id: int,
    git_repo: str,
    dockerfile_path: str = "Dockerfile"
):
    """
    1. Git 저장소 클론
    2. Docker 이미지 빌드
    3. Kubernetes Deployment 생성
    4. Service/Ingress 자동 설정
    5. 도메인 자동 할당
    """
    pass
```

**구현 필요 사항:**
- [ ] GitOps 통합 (ArgoCD, Flux)
- [ ] 자동 Docker 빌드 (Kaniko, Buildah)
- [ ] Kubernetes Deployment 자동 생성
- [ ] Ingress/LoadBalancer 자동 설정
- [ ] SSL 인증서 자동 발급 (cert-manager)

---

### 2. CI/CD 파이프라인 ❌

**현재 상태:**
- GitHub Actions는 있지만 Monewment 플랫폼 자체에는 없음

**필요한 기능:**
```python
class DeploymentPipeline(Base):
    """CI/CD 파이프라인 정의"""
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    # Git 설정
    git_repo = Column(String)
    git_branch = Column(String, default="main")
    
    # 빌드 설정
    build_command = Column(String)
    dockerfile_path = Column(String)
    
    # 배포 설정
    deploy_strategy = Column(String)  # rolling, blue-green, canary
    auto_deploy = Column(Boolean, default=False)
```

**구현 필요 사항:**
- [ ] Webhook 수신 (Git push 이벤트)
- [ ] 자동 빌드 트리거
- [ ] 테스트 자동 실행
- [ ] 배포 전략 (Rolling, Blue-Green, Canary)
- [ ] 롤백 기능

---

### 3. 서비스 메시 및 네트워킹 ❌

**현재 상태:**
- VM 간 통신 설정 없음
- 외부 접근 설정 수동

**필요한 기능:**
```python
class ServiceEndpoint(Base):
    """서비스 엔드포인트 관리"""
    vm_id = Column(Integer, ForeignKey("vm_instances.id"))
    
    # 네트워크 설정
    internal_port = Column(Integer)
    external_port = Column(Integer)
    protocol = Column(String, default="HTTP")
    
    # 도메인 설정
    subdomain = Column(String)  # user-app.monewment.io
    ssl_enabled = Column(Boolean, default=True)
```

**구현 필요 사항:**
- [ ] Istio/Linkerd 서비스 메시
- [ ] 자동 DNS 설정
- [ ] Load Balancer 자동 구성
- [ ] SSL/TLS 자동 관리
- [ ] API Gateway 통합

---

### 4. 오토스케일링 ❌

**현재 상태:**
- VM 수동 생성/삭제만 가능

**필요한 기능:**
```python
class AutoScalingPolicy(Base):
    """오토스케일링 정책"""
    vm_id = Column(Integer, ForeignKey("vm_instances.id"))
    
    # 스케일링 조건
    min_instances = Column(Integer, default=1)
    max_instances = Column(Integer, default=10)
    
    # 메트릭 기반 스케일링
    cpu_threshold = Column(Integer, default=80)  # %
    memory_threshold = Column(Integer, default=80)  # %
    request_per_second_threshold = Column(Integer)
```

**구현 필요 사항:**
- [ ] Horizontal Pod Autoscaler (HPA)
- [ ] Vertical Pod Autoscaler (VPA)
- [ ] Cluster Autoscaler
- [ ] 메트릭 수집 (Prometheus)
- [ ] 예측 기반 스케일링

---

### 5. 데이터베이스 자동 프로비저닝 ❌

**현재 상태:**
- 애플리케이션 VM만 생성 가능
- DB는 사용자가 직접 설치

**필요한 기능:**
```python
class ManagedDatabase(Base):
    """관리형 데이터베이스"""
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    # DB 타입
    db_type = Column(String)  # postgres, mysql, mongodb, redis
    version = Column(String)
    
    # 리소스
    storage_gb = Column(Integer)
    backup_enabled = Column(Boolean, default=True)
    
    # 연결 정보
    connection_string = Column(String)
```

**구현 필요 사항:**
- [ ] PostgreSQL Operator
- [ ] MySQL Operator
- [ ] MongoDB Operator
- [ ] Redis Operator
- [ ] 자동 백업 및 복구
- [ ] 고가용성 (Replication)

---

### 6. 모니터링 및 알림 ❌

**현재 상태:**
- Prometheus 메트릭만 수집
- 알림 시스템 없음

**필요한 기능:**
```python
class AlertRule(Base):
    """알림 규칙"""
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    # 조건
    metric_name = Column(String)
    threshold = Column(Float)
    duration_seconds = Column(Integer)
    
    # 알림 채널
    notification_channels = Column(JSON)  # ["slack", "email"]
```

**구현 필요 사항:**
- [ ] Grafana 대시보드 자동 생성
- [ ] AlertManager 통합
- [ ] Slack/Email/SMS 알림
- [ ] 로그 집계 (Loki)
- [ ] APM (Application Performance Monitoring)

---

### 7. 셀프 서비스 마켓플레이스 ❌

**현재 상태:**
- 수동 설치만 가능

**필요한 기능:**
```python
class MarketplaceApp(Base):
    """마켓플레이스 앱 템플릿"""
    name = Column(String)  # "WordPress", "GitLab", "Nextcloud"
    category = Column(String)  # "CMS", "DevOps", "Storage"
    
    # Helm Chart 정보
    helm_repo = Column(String)
    helm_chart = Column(String)
    default_values = Column(JSON)
    
    # 리소스 요구사항
    min_cpu = Column(Integer)
    min_memory_gb = Column(Integer)
```

**구현 필요 사항:**
- [ ] Helm Chart 저장소
- [ ] 원클릭 앱 설치
- [ ] 앱 업데이트 관리
- [ ] 앱 간 의존성 관리

---

## 🎯 자율주행 호스팅 로드맵

### Phase 1: 기본 자동화 (2주)
```
[ ] GitOps 통합
  [ ] ArgoCD 설치
  [ ] Git 저장소 연동
  [ ] 자동 배포 파이프라인

[ ] 네트워킹 자동화
  [ ] Ingress Controller 설정
  [ ] cert-manager 설치
  [ ] 자동 도메인 할당
```

### Phase 2: CI/CD (2주)
```
[ ] Tekton/Jenkins 통합
  [ ] Webhook 수신
  [ ] 자동 빌드
  [ ] 자동 테스트
  [ ] 배포 전략 구현
```

### Phase 3: 관리형 서비스 (3주)
```
[ ] Database Operators
  [ ] PostgreSQL
  [ ] Redis
  [ ] MongoDB

[ ] 오토스케일링
  [ ] HPA 설정
  [ ] Cluster Autoscaler
```

### Phase 4: 모니터링 및 최적화 (2주)
```
[ ] Grafana 대시보드
[ ] AlertManager
[ ] 로그 집계
[ ] 비용 최적화
```

---

## 💡 즉시 구현 가능한 개선

### 1. 자동 배포 API 추가
```python
# src/api/v1/endpoints/deploy.py
@router.post("/auto-deploy")
async def auto_deploy(
    project_id: int,
    git_repo: str,
    branch: str = "main"
):
    """
    Git 저장소에서 자동으로 서비스 배포
    """
    # 1. Git 클론
    # 2. Dockerfile 감지
    # 3. 이미지 빌드
    # 4. Kubernetes Deployment 생성
    # 5. Service/Ingress 생성
    pass
```

### 2. 도메인 자동 할당
```python
class ServiceDomain(Base):
    """서비스 도메인 관리"""
    vm_id = Column(Integer, ForeignKey("vm_instances.id"))
    subdomain = Column(String)  # {project-name}.monewment.io
    ssl_cert_id = Column(String)
```

### 3. 환경 변수 관리
```python
class EnvironmentVariable(Base):
    """환경 변수 보안 저장"""
    project_id = Column(Integer, ForeignKey("projects.id"))
    key = Column(String)
    value_encrypted = Column(String)  # 암호화된 값
```

---

## 📋 현재 vs 이상적 상태

| 기능 | 현재 | 이상적 상태 | 우선순위 |
|------|------|-------------|----------|
| VM 프로비저닝 | ✅ 구현됨 | ✅ 완료 | - |
| 자동 배포 | ❌ 없음 | ✅ Git → 자동 배포 | 🔴 High |
| CI/CD | ❌ 없음 | ✅ 자동 빌드/테스트 | 🔴 High |
| 네트워킹 | 🟡 수동 | ✅ 자동 도메인/SSL | 🟠 Medium |
| 오토스케일링 | ❌ 없음 | ✅ 메트릭 기반 | 🟠 Medium |
| 관리형 DB | ❌ 없음 | ✅ 원클릭 DB | 🟠 Medium |
| 모니터링 | 🟡 기본 | ✅ 대시보드/알림 | 🟢 Low |
| 마켓플레이스 | ❌ 없음 | ✅ 앱 스토어 | 🟢 Low |

---

## 🎓 결론

### 현재 상태
**"클러스터를 이식받아 가상 공간 만들고 거기에 서비스 개발해서 붙여넣는 호스팅"**

✅ **맞습니다!** 하지만 현재는:
- ✅ 클러스터 관리 (Cluster 모델)
- ✅ VM 생성 (KubeVirt 통합)
- ✅ 리소스 할당 (Organization, Quota)
- ❌ **자동 서비스 배포는 없음** (수동 설치 필요)

### 자율주행으로 가려면
1. **GitOps 통합** - 코드 푸시 → 자동 배포
2. **CI/CD 파이프라인** - 자동 빌드/테스트
3. **네트워킹 자동화** - 도메인/SSL 자동 설정
4. **관리형 서비스** - DB, 캐시 원클릭 생성
5. **오토스케일링** - 트래픽에 따라 자동 확장

**권장:** Phase 1 (GitOps + 네트워킹)부터 시작하면 2주 내에 기본 자동 배포 가능!
