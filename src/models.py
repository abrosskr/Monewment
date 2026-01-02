from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum, JSON
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
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    plan_type = Column(String, default="basic") # basic, pro, team
    
    users = relationship("User", back_populates="organization")
    rooms = relationship("Room", back_populates="organization")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.MEMBER) # 계급장
    
    org_id = Column(Integer, ForeignKey("organizations.id"))
    organization = relationship("Organization", back_populates="users")

class PolicyPreset(Base):
    __tablename__ = "policy_presets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) # 예: "가성비 모드", "보안 모드"
    rules = Column(JSON, nullable=False)  # {"limit": 50, "models": ["gpt-4"]}
    
    rooms = relationship("Room", back_populates="policy")

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) # 예: "개발팀 룸 1"
    status = Column(Enum(RoomStatus), default=RoomStatus.ACTIVE)
    k8s_namespace = Column(String, unique=True) # 실제 클러스터 연결 고리
    
    org_id = Column(Integer, ForeignKey("organizations.id"))
    organization = relationship("Organization", back_populates="rooms")
    
    policy_id = Column(Integer, ForeignKey("policy_presets.id"))
    policy = relationship("PolicyPreset", back_populates="rooms")
    
    logs = relationship("AuditLog", back_populates="room")

class AuditLog(Base):
    """
    수정 불가능한(Immutable) 블랙박스 로그
    """
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    action_type = Column(String, nullable=False) # EXECUTE, POLICY_CHANGE
    details = Column(JSON) # 프롬프트 내용, 비용 등
    
    room_id = Column(Integer, ForeignKey("rooms.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    room = relationship("Room", back_populates="logs")