from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum, JSON, Numeric
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum

# SQLAlchemy 기본 클래스 생성
Base = declarative_base()

# --- Enums (선택지) ---
class UserRole(str, enum.Enum):
    OWNER = "OWNER"   # 사장 (결제, 전체 관리)
    ADMIN = "ADMIN"   # 관리자 (정책 설정)
    MEMBER = "MEMBER" # 직원 (사용만 가능)

class RoomStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"       # 정상 (Yellow Block)
    WARNING = "WARNING"     # 경고
    SUSPENDED = "SUSPENDED" # 차단 (Red)

# --- Tables ---

class Organization(Base):
    """
    [ProjectClient] 법인격 껍데기
    - 실제 결제와 프로젝트 소유의 주체입니다.
    """
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    plan_type = Column(String, default="basic") # basic, pro, team
    
    users = relationship("User", back_populates="organization")
    rooms = relationship("Room", back_populates="organization")
    projects = relationship("Project", back_populates="organization")
    
    # [신규] 계층 및 쿼터 관리
    cluster_id = Column(Integer, ForeignKey("clusters.id"), nullable=True)
    cluster = relationship("Cluster", back_populates="organizations")
    
    quota_cpu = Column(Integer, default=10)
    quota_ram_gb = Column(Integer, default=32)
    quota_gpu = Column(Integer, default=0)
    
    status = Column(String, default="ACTIVE") # PENDING, ACTIVE, SUSPENDED, DELETED

class User(Base):
    """
    [GeneralUser] 실제 사용자
    - 법인에 소속되어 권한을 행사하는 주체입니다.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.MEMBER) # 시스템 전체 계급장
    
    org_id = Column(Integer, ForeignKey("organizations.id"))
    organization = relationship("Organization", back_populates="users")
    
    # [신규] 내가 소속된 프로젝트 멤버십 목록
    memberships = relationship("ProjectMember", back_populates="user")

class Project(Base):
    """
    [신규 추가] 프로젝트 메타데이터
    - 파일 시스템의 폴더와 1:1 매칭되며, 설치된 기능(Marketplace) 정보를 담습니다.
    """
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False) # 폴더명과 일치
    status = Column(String, default="ACTIVE") # PENDING, ACTIVE, SUSPENDED
    
    # 소속 법인 (ProjectClient)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    organization = relationship("Organization", back_populates="projects")
    
    # 설치된 기능 목록 (예: ["logs", "auto-doc", "mcp-bot"])
    installed_features = Column(JSON, default=["logs"])

    # [신규] 프로젝트에 소속된 팀원 목록
    members = relationship("ProjectMember", back_populates="project")

class ProjectMember(Base):
    """
    [신규 추가] 프로젝트 멤버 (매핑 테이블)
    - 어떤 유저가 어떤 프로젝트에서 무슨 권한을 갖는지 정의합니다.
    """
    __tablename__ = "project_members"
    id = Column(Integer, primary_key=True, index=True)
    
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # 프로젝트 내 역할 (ADMIN: 관리자, MEMBER: 일반, VIEWER: 읽기전용)
    role = Column(String, default="MEMBER")
    
    # 세부 허용 기능 (예: {"can_delete_logs": true})
    allowed_features = Column(JSON, default={})
    
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="memberships")

class Cluster(Base):
    """
    [Infrastructure] 물리적/논리적 리소스 클러스터
    - Super Admin이 관리하며, 여러 Organization이 이 클러스터를 공유하거나 전용으로 사용합니다.
    """
    __tablename__ = "clusters"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    region = Column(String, default="kr-seoul-1")
    status = Column(String, default="ACTIVE") # ACTIVE, MAINTENANCE, DOWN
    
    # 하드웨어 용량 (총량)
    cpu_capacity = Column(Integer, default=100)
    ram_capacity_gb = Column(Integer, default=512)
    gpu_capacity = Column(Integer, default=8)
    
    organizations = relationship("Organization", back_populates="cluster")

class PolicyPreset(Base):
    __tablename__ = "policy_presets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) 
    rules = Column(JSON, nullable=False)  
    
    rooms = relationship("Room", back_populates="policy")

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) 
    status = Column(Enum(RoomStatus), default=RoomStatus.ACTIVE)
    k8s_namespace = Column(String, unique=True) 
    
    org_id = Column(Integer, ForeignKey("organizations.id"))
    organization = relationship("Organization", back_populates="rooms")
    
    policy_id = Column(Integer, ForeignKey("policy_presets.id"))
    policy = relationship("PolicyPreset", back_populates="rooms")
    
    logs = relationship("AuditLog", back_populates="room")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    action_type = Column(String, nullable=False) 
    details = Column(JSON) 
    
    room_id = Column(Integer, ForeignKey("rooms.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    room = relationship("Room", back_populates="logs")
# --- Phase 4: Metering & Billing Models ---

class SubscriptionPlan(Base):
    """
    [Billing] 월 정액 구독 플랜 (Product)
    예: Starter($0), Pro($50), Enterprise($200)
    """
    __tablename__ = "subscription_plans"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    price = Column(Numeric(10, 2), nullable=False) # 월 가격
    monthly_credits = Column(Numeric(10, 2), default=0) # 기본 제공 크레딧 ($)
    allowed_flavors = Column(JSON, default=[]) # 허용된 VMFlavor ID 목록
    is_active = Column(Boolean, default=True)

class ProjectSubscription(Base):
    """
    [Billing] 프로젝트별 구독 현황
    """
    __tablename__ = "project_subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    
    project_id = Column(Integer, ForeignKey("projects.id"), unique=True)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"))
    
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    next_billing_date = Column(DateTime(timezone=True))
    status = Column(String, default="ACTIVE") # ACTIVE, PAST_DUE, CANCELLED
    
    # [Guardrails] Hard Cap (예산 한도, NULL이면 무제한)
    usage_limit_hard_cap = Column(Numeric(10, 2), nullable=True)

    project = relationship("Project", backref="subscription")
    plan = relationship("SubscriptionPlan")

class ProjectBudget(Base):
    """
    [Guardrails] 프로젝트별 예산 설정 및 현재 사용량 캐싱
    """
    __tablename__ = "project_budgets"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), unique=True)
    
    alert_threshold = Column(Numeric(10, 2), default=50.00) # 알림 기준 ($)
    current_month_spend = Column(Numeric(10, 2), default=0.00) # 현재 사용량 캐시

    project = relationship("Project", backref="budget")

class VMFlavor(Base):
    """
    [Billing] VM 하드웨어 상품 (Pricing Catalog)
    """
    __tablename__ = "vm_flavors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) # e.g. "AI Research Station"
    channel = Column(String, nullable=False) # GAMING, RND
    spec_tier = Column(String, nullable=False) # HIGH, MID
    
    cpu_cores = Column(Integer, nullable=False)
    memory_gb = Column(Integer, nullable=False)
    gpu_model = Column(String, nullable=True)
    
    hourly_rate = Column(Numeric(10, 4), nullable=False) # 시간당 요금 ($)
    is_active = Column(Boolean, default=True)

class AIModel(Base):
    """
    [Billing] AI 모델 소프트웨어 상품 (Pricing Catalog)
    """
    __tablename__ = "ai_models"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) # e.g. "GPT-4-Turbo"
    hourly_surcharge = Column(Numeric(10, 4), default=0.0000) # 추가 요금
    is_active = Column(Boolean, default=True)

class VMInstance(Base):
    """
    [Resource] 생성된 가상머신 (Business Object)
    - KubeVirt VMI와 1:1 매핑되지만, DB에 영구 기록됨.
    """
    __tablename__ = "vm_instances"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # K8s Resource Name
    
    project_id = Column(Integer, ForeignKey("projects.id"))
    flavor_id = Column(Integer, ForeignKey("vm_flavors.id"))
    
    status = Column(String, default="PROVISIONING") # PROVISIONING, RUNNING, STOPPED, TERMINATED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    project = relationship("Project", backref="vms")
    flavor = relationship("VMFlavor")

class VMUsage(Base):
    """
    [Billing] 과금 이력 세션 (Immutable History)
    모델이나 Flavor가 변경되면 새 레코드가 생성됨.
    """
    __tablename__ = "vm_usage"
    id = Column(Integer, primary_key=True, index=True)
    
    vm_id = Column(Integer, ForeignKey("vm_instances.id"))
    ai_model_id = Column(Integer, ForeignKey("ai_models.id"), nullable=True)
    
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, default=0)
    
    # [Snapshot Pricing] 세션 시작 시점의 가격 박제
    applied_hw_rate = Column(Numeric(10, 4), nullable=False)
    applied_model_rate = Column(Numeric(10, 4), default=0.0000)
    
    total_cost = Column(Numeric(10, 4), default=0.0000)

    vm = relationship("VMInstance", backref="usage_history")
    ai_model = relationship("AIModel")
