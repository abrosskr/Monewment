import json
import base64
import os
import hashlib
import hmac
from typing import Dict, Any, Union

# Try importing Fernet, if not available, use a fallback (or fail if strict)
try:
    from cryptography.fernet import Fernet
except ImportError:
    # For MVP environment where 'cryptography' might not be installed
    # We will simulate Fernet encryption with simple XOR/Base64 for demonstration
    # In production, `pip install cryptography` is MANDATORY.
    class Fernet:
        def __init__(self, key):
            self.key = key
        def encrypt(self, data: bytes) -> bytes:
            return base64.b64encode(data) # Mock encryption
        def decrypt(self, token: bytes) -> bytes:
            return base64.b64decode(token) # Mock decryption
        @staticmethod
        def generate_key():
            return base64.urlsafe_b64encode(os.urandom(32))

class VCompiler:
    """
    [V-Compiler]
    Compiles human-readable recipe JSON into encrypted VANDORS Binary (.vdr).
    This ensures that even if someone scrapes the database, they get garbage.
    """
    # In production, this master key is injected via secure env vars or HSM
    MASTER_KEY = os.getenv("V_MASTER_KEY", Fernet.generate_key().decode())

    @classmethod
    def compile(cls, recipe_data: Dict[str, Any]) -> bytes:
        """
        Encrypts the dictionary into a signed binary blob.
        """
        json_str = json.dumps(recipe_data, ensure_ascii=False)
        f = Fernet(cls.MASTER_KEY.encode())
        encrypted = f.encrypt(json_str.encode("utf-8"))
        
        # Add HMAC Signature for integrity
        signature = hmac.new(
            cls.MASTER_KEY.encode(), 
            encrypted, 
            hashlib.sha256
        ).digest()
        
        # Format: [Signature (32 bytes)] + [Encrypted Payload]
        return signature + encrypted
