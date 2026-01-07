import os
import secrets
from typing import Tuple, List, Dict
from src.core.ant_security import AntSecurity
from src.common.erasure_coding import ErasureCoding

class VaultShredder:
    def __init__(self):
        self.ec = ErasureCoding(n=10, m=4)

    def process_file(self, file_path: str) -> Dict:
        """
        Reads file -> Encrypts -> Shards.
        Returns metadata including shards (in-memory for V1) and key.
        """
        # 1. Read File
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(file_path, "rb") as f:
            raw_data = f.read()
            
        # 2. Encrypt (AES-256)
        # Generate a random 32-byte key for this file
        file_key = AntSecurity.generate_key()
        security = AntSecurity(file_key)
        
        # We need to encrypt raw bytes, but AntSecurity is designed for JSON payloads (Base64).
        # Let's reuse AESGCM primitive directly or extend AntSecurity.
        # For now, we will use the internal AESGCM from AntSecurity if accessible, or just create new.
        
        nonce = os.urandom(12)
        ciphertext = security.aesgcm.encrypt(nonce, raw_data, None)
        
        # Bundle Nonce + Ciphertext for storage
        encrypted_blob = nonce + ciphertext
        
        # 3. Erasure Coding (Split)
        shards = self.ec.encode(encrypted_blob)
        
        # 4. Result
        return {
            "key": file_key.hex(),
            "file_size": len(raw_data),
            "encrypted_size": len(encrypted_blob),
            "shards": shards, # List[bytes]
            "shard_count": len(shards)
        }

    def recover_file(self, shards: List[bytes], key_hex: str, original_size: int = None) -> bytes:
        """
        Shards -> Reassemble (EC) -> Decrypt -> Raw Data
        """
        # 1. EC Decode
        try:
            encrypted_blob = self.ec.decode(shards)
            # Remove padding if size is known
            if original_size is not None:
                encrypted_blob = encrypted_blob[:original_size]
        except Exception as e:
            raise ValueError(f"Erasure Coding Recovery Failed: {e}")
            
        # 2. Decrypt
        nonce = encrypted_blob[:12]
        ciphertext = encrypted_blob[12:]
        
        file_key = bytes.fromhex(key_hex)
        security = AntSecurity(file_key)
        
        plaintext = security.aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext
