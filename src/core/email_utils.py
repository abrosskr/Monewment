import secrets
import logging
from email_validator import validate_email, EmailNotValidError
from src.core.redis_client import RedisManager

logger = logging.getLogger("uvicorn")

class EmailUtils:
    @staticmethod
    def validate_format(email: str) -> bool:
        """이메일 형식이 유효한지 검사합니다."""
        try:
            validate_email(email, check_deliverability=False)
            return True
        except EmailNotValidError:
            return False

    @staticmethod
    async def send_verification_email(email: str) -> str:
        """
        인증 코드를 생성하고 발송합니다.
        (현재는 Console에 로그를 찍는 Mock 방식입니다.)
        """
        # 1. Generate 6-digit code
        code = secrets.randbelow(1000000)
        code_str = f"{code:06d}"
        
        # 2. Store in Redis (TTL: 5 min)
        redis = RedisManager.get_instance().get_client()
        if redis:
            await redis.setex(f"email_verif:{email}", 300, code_str)
        else:
            logger.warning("Redis not available. Verification code not stored.")

        # 3. Send (Mock)
        logger.info(f"📧 [Mock Email] To: {email} | Subject: Verification Code | Body: Your code is [{code_str}]")
        
        return code_str

    @staticmethod
    async def verify_code(email: str, code: str) -> bool:
        """저장된 인증 코드와 일치하는지 확인합니다."""
        redis = RedisManager.get_instance().get_client()
        if not redis:
            return False
            
        stored = await redis.get(f"email_verif:{email}")
        if stored and stored == code:
            # 인증 성공 시 키 삭제 (일회용)
            await redis.delete(f"email_verif:{email}")
            return True
        return False
