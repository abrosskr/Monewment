from typing import Dict, Any, Optional
import json
import hashlib
import hmac
from .v_compiler import VCompiler, Fernet # Re-use Fernet/Keys from Compiler context

class VKernel:
    """
    [V-Kernel]
    The only entity authorized to unlock .vdr files.
    Decryption happens IN-MEMORY only.
    """
    @classmethod
    def load(cls, vdr_blob: bytes) -> Dict[str, Any]:
        """
        Verifies signature and decrypts the blob.
        Raises SecurityException if tampered.
        """
        # 1. Split Signature and Payload
        signature = vdr_blob[:32]
        payload = vdr_blob[32:]
        
        # 2. Verify Integrity
        expected_sig = hmac.new(
            VCompiler.MASTER_KEY.encode(), 
            payload, 
            hashlib.sha256
        ).digest()
        
        if not hmac.compare_digest(signature, expected_sig):
            raise SecurityException("TAMPER ALERT: Recipe file integrity check failed!")
            
        # 3. Decrypt
        f = Fernet(VCompiler.MASTER_KEY.encode())
        try:
            json_str = f.decrypt(payload).decode("utf-8")
            return json.loads(json_str)
        except Exception as e:
            raise SecurityException(f"DECRYPTION FAILED: Invalid key or corrupt data. {str(e)}")

class SecurityException(Exception):
    pass
