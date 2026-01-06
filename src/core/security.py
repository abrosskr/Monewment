import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.config import settings
from src.database import SessionLocal
from src.models import User
from src.dependencies import get_db

# OAuth2 스킴 설정 (FastAPI 자동 문서화 및 클라이언트 연동용)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def hash_password(password: str) -> str:
    """평문 비밀번호를 Bcrypt 해시로 변환합니다."""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """평문 비밀번호와 해시된 비밀번호가 일치하는지 검증합니다."""
    try:
        pwd_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """사용자 정보를 담은 서명된 JWT 토큰을 생성합니다."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """요청 헤더의 JWT 토큰을 검증하고 현재 사용자 정보를 반환합니다."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="검증할 수 없는 자격 증명입니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def validate_project_path(project_name: str) -> Path:
    """
    Project 이름이 유효한지 검사하고, 상위 폴더 접근(Path Traversal)을 차단합니다.
    Strictly confining operations within settings.PROJECTS_DIR.
    """
    # 1. 특수문자 및 공백 제거 (Sanitization)
    clean_name = "".join(c for c in project_name if c.isalnum() or c in ("-", "_")).strip()
    if not clean_name:
        raise HTTPException(status_code=400, detail="유효하지 않은 프로젝트 이름입니다.")

    # 2. 경로 조합 및 정규화 (Normalization)
    base_dir = settings.PROJECTS_DIR.resolve()
    target_path = (base_dir / clean_name).resolve()

    # 3. 경계 검사 (Boundary Check)
    # 정규화된 타겟 경로가 반드시 프로젝트 루트 디렉토리 안에 있어야 함.
    if not str(target_path).startswith(str(base_dir)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="허용되지 않은 경로 접근입니다."
        )

    return target_path
