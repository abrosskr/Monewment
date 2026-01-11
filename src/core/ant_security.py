import os
import json
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from typing import Dict, Any, Union

class AntSecurity:
    def __init__(self, key_bytes: bytes = None):
        """
        Initialize with a 32-byte (256-bit) key.
        If no key is provided, loads from ANT_ENCRYPTION_KEY environment variable.
        """
        if key_bytes:
            if len(key_bytes) != 32:
                raise ValueError("AES-256 requires a 32-byte key.")
            self.aesgcm = AESGCM(key_bytes)
        else:
            # Load from environment variable
            from src.config import settings
            key_hex = settings.ANT_ENCRYPTION_KEY
            
            if not key_hex:
                raise RuntimeError(
                    "ANT_ENCRYPTION_KEY environment variable not set. "
                    "Generate one with: python scripts/generate_keys.py"
                )
            
            try:
                key_bytes = bytes.fromhex(key_hex)
                if len(key_bytes) != 32:
                    raise ValueError("ANT_ENCRYPTION_KEY must be 32 bytes (64 hex characters)")
                self.aesgcm = AESGCM(key_bytes)
            except ValueError as e:
                raise RuntimeError(f"Invalid ANT_ENCRYPTION_KEY format: {e}")


    @staticmethod
    def generate_key() -> bytes:
        return AESGCM.generate_key(bit_length=256)

    def encrypt_payload(self, data: Dict[str, Any]) -> str:
        """
        Encrypts a dictionary payload into a base64 encoded string.
        Format: version|nonce|ciphertext (all base64 encoded and joined by |)
        """
        if not self.aesgcm:
            raise RuntimeError("Encryption key not set.")

        # 1. Serialize
        json_bytes = json.dumps(data).encode('utf-8')
        
        # 2. Generate Nonce (12 bytes for GCM)
        nonce = os.urandom(12)
        
        # 3. Encrypt
        ciphertext = self.aesgcm.encrypt(nonce, json_bytes, None)
        
        # 4. Pack
        # We start with "v1" to allow future versioning
        return f"v1|{base64.b64encode(nonce).decode('utf-8')}|{base64.b64encode(ciphertext).decode('utf-8')}"

    def decrypt_payload(self, token: str) -> Dict[str, Any]:
        """
        Decrypts a token string back into a dictionary.
        """
        if not self.aesgcm:
            raise RuntimeError("Encryption key not set.")

        try:
            parts = token.split('|')
            if len(parts) != 3 or parts[0] != 'v1':
                raise ValueError("Invalid token format")
            
            nonce = base64.b64decode(parts[1])
            ciphertext = base64.b64decode(parts[2])
            
            # Decrypt
            plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
            return json.loads(plaintext.decode('utf-8'))
            
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
