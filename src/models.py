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
    projects = relationship("Project", back_populates="organization") # [신규] 프로젝트 목록

class User(Base):
    """
    [GeneralUser] 실제 사용자
    - 법인에 소속되어 권한을 행사하는 주체입니다.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.MEMBER) # 계급장
    
    org_id = Column(Integer, ForeignKey("organizations.id"))
    organization = relationship("Organization", back_populates="users")

class Project(Base):
    """
    [신규 추가] 프로젝트 메타데이터
    - 파일 시스템의 폴더와 1:1 매칭되며, 설치된 기능(Marketplace) 정보를 담습니다.
    """
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False) # 폴더명과 일치
    
    # 소속 법인 (ProjectClient)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    organization = relationship("Organization", back_populates="projects")
    
    # 설치된 기능 목록 (예: ["logs", "auto-doc", "mcp-bot"])
    installed_features = Column(JSON, default=["logs"])

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