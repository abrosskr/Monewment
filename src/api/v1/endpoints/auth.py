from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.dependencies import get_db
from src.models import User
from src.schemas import SignupRequest, LoginRequest
from src.core.security import hash_password, verify_password, create_access_token, get_current_user
from src.core.limiter import limiter

router = APIRouter()

@router.post("/signup")
@limiter.limit("3/minute")
async def signup(request: Request, req: SignupRequest, db: AsyncSession = Depends(get_db)):
    """새로운 사용자를 등록하고 OWNER 권한을 부여합니다."""
    result = await db.execute(select(User).where(User.email == req.email))
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")
    
    hashed = hash_password(req.password)
    new_user = User(email=req.email, hashed_password=hashed, role="OWNER")
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"status": "success", "user_id": new_user.id, "message": "가입이 완료되었습니다."}

@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, req: LoginRequest, db: AsyncSession = Depends(get_db)):
    print(f"DEBUG: Login Request for {req.email}")
    """이메일과 비밀번호를 검증하고 액세스 권한을 부여합니다."""
    try:
        result = await db.execute(select(User).where(User.email == req.email))
        user = result.scalars().first()
        
        if not user or not verify_password(req.password, user.hashed_password):
            print("DEBUG: Auth Failed")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="아이디 또는 비밀번호가 잘못되었습니다.")
        
        print("DEBUG: Auth Success, Generating Token...")
        # Generate JWT Token
        access_token = create_access_token(data={"sub": user.email})
        print(f"DEBUG: Token Generated: {access_token[:10]}...")
        
        return {
            "status": "success", 
            "user_id": user.id, 
            "name": user.email.split("@")[0], 
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        print(f"DEBUG: Login Endpoint Error: {e}")
        import traceback
        traceback.print_exc()
        raise e

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """현재 로그인된 사용자의 정보를 반환합니다 (JWT 검증)."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role
    }

from src.core.security import generate_api_key, hash_api_key

@router.post("/api-key")
async def create_api_key(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    [Security] 새로운 API Key를 발급합니다.
    - 기존 키는 무효화됩니다.
    - 발급된 키는 한 번만 보여지며, DB에는 해시값만 저장됩니다.
    """
    # 1. Generate Safe Key
    new_key = generate_api_key()
    
    # 2. Hash Key
    hashed_key = hash_api_key(new_key)
    
    # 3. Save Hash to DB
    current_user.api_key = hashed_key
    await db.commit()
    
    return {
        "status": "success",
        "message": "새로운 API Key가 발급되었습니다. 이 키는 다시 조회할 수 없으니 안전한 곳에 저장하세요.",
        "api_key": new_key
    }
