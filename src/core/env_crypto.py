"""
환경 변수 암호화/복호화 유틸리티
"""
from cryptography.fernet import Fernet
from src.config import settings

class EnvCrypto:
    """환경 변수 암호화/복호화"""
    
    def __init__(self):
        # ANT_ENCRYPTION_KEY 재사용 (32바이트)
        key_hex = settings.ANT_ENCRYPTION_KEY
        key_bytes = bytes.fromhex(key_hex)
        
        # Fernet은 32바이트 키를 Base64 인코딩한 값이 필요
        import base64
        fernet_key = base64.urlsafe_b64encode(key_bytes)
        self.cipher = Fernet(fernet_key)
    
    def encrypt(self, value: str) -> str:
        """값 암호화"""
        if not value:
            return ""
        return self.cipher.encrypt(value.encode()).decode()
    
    def decrypt(self, encrypted: str) -> str:
        """값 복호화"""
        if not encrypted:
            return ""
        return self.cipher.decrypt(encrypted.encode()).decode()

# 싱글톤 인스턴스
env_crypto = EnvCrypto()
