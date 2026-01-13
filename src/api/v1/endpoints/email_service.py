from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from src.core.email_utils import EmailUtils

router = APIRouter()

class EmailRequest(BaseModel):
    email: EmailStr

class VerifyRequest(BaseModel):
    email: EmailStr
    code: str

@router.post("/validate")
async def validate_email_format(req: EmailRequest):
    """이메일 주소의 형식이 올바른지 검사합니다."""
    is_valid = EmailUtils.validate_format(req.email)
    return {"valid": is_valid, "email": req.email}

@router.post("/send-verification")
async def send_verification(req: EmailRequest):
    """
    이메일로 인증 코드를 발송합니다.
    (현재 시스템은 Mock Sender를 사용하므로, 서버 로그에서 코드를 확인하세요.)
    """
    if not EmailUtils.validate_format(req.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    await EmailUtils.send_verification_email(req.email)
    return {
        "status": "success", 
        "message": f"Verification code sent to {req.email}",
        "note": "Check server console for the code (Mock Mode)"
    }

@router.post("/verify-code")
async def verify_code(req: VerifyRequest):
    """이메일 인증 코드를 검증합니다."""
    is_valid = await EmailUtils.verify_code(req.email, req.code)
    
    if is_valid:
        return {"status": "success", "verified": True}
    else:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
