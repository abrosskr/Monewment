import pytest
import asyncio
from src.core.ant_security import AntSecurity

def test_ant_security_encryption_decryption():
    # 1. Setup
    key = AntSecurity.generate_key()
    assert len(key) == 32
    
    security = AntSecurity(key)
    
    payload = {
        "type": "heartbeat",
        "status": "ONLINE",
        "gpu": "RTX_4090"
    }
    
    # 2. Encrypt
    token = security.encrypt_payload(payload)
    assert isinstance(token, str)
    assert token.startswith("v1|")
    
    # 3. Decrypt
    decrypted_payload = security.decrypt_payload(token)
    assert decrypted_payload == payload
    assert decrypted_payload["gpu"] == "RTX_4090"

def test_ant_security_invalid_token():
    key = AntSecurity.generate_key()
    security = AntSecurity(key)
    
    with pytest.raises(ValueError):
        security.decrypt_payload("invalid_token_format")

def test_ant_security_wrong_key():
    key1 = AntSecurity.generate_key()
    key2 = AntSecurity.generate_key()
    
    sec1 = AntSecurity(key1)
    sec2 = AntSecurity(key2)
    
    payload = {"data": "secret"}
    token = sec1.encrypt_payload(payload)
    
    # Decrypt with wrong key should fail (MAC verification failed)
    with pytest.raises(ValueError):
        sec2.decrypt_payload(token)
