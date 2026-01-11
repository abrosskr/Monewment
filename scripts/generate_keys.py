#!/usr/bin/env python3
"""
보안 키 생성 스크립트
Monewment 프로젝트의 .env 파일에 필요한 보안 키들을 생성합니다.
"""
import secrets

def generate_keys():
    """필요한 모든 보안 키를 생성하고 출력합니다."""
    print("=" * 60)
    print("Monewment Security Keys Generator")
    print("=" * 60)
    print("\n아래 키들을 .env 파일에 복사하세요:\n")
    
    # JWT Secret Key (32 bytes = 43 characters in base64)
    secret_key = secrets.token_urlsafe(32)
    print(f"SECRET_KEY={secret_key}")
    
    # Ant Encryption Key (32 bytes = 64 hex characters)
    encryption_key = secrets.token_hex(32)
    print(f"ANT_ENCRYPTION_KEY={encryption_key}")
    
    # PostgreSQL Password (16 bytes = 22 characters in base64)
    postgres_password = secrets.token_urlsafe(16)
    print(f"POSTGRES_PASSWORD={postgres_password}")
    
    print("\n" + "=" * 60)
    print("⚠️  중요: 이 키들을 안전하게 보관하세요!")
    print("=" * 60)

if __name__ == "__main__":
    generate_keys()
