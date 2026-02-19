import os
import httpx
import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv() # Load injected .env
try:
    from ..protocol.fis_schema import RegisterRequest, RegisterResponse
except (ImportError, ValueError):
    from core.protocol.fis_schema import RegisterRequest, RegisterResponse

logger = logging.getLogger("Handshake")
logging.basicConfig(level=logging.INFO)

class EdenvaleHandshake:
    """
    [The Security Handshake]
    Executed by external instances to register with the Master.
    """
    def __init__(self):
        self.master_url = os.getenv("MASTER_API_URL")
        self.instance_id = os.getenv("INSTANCE_ID")
        self.instance_key = os.getenv("INSTANCE_KEY")
        self.access_token = None

    async def initiate(self) -> bool:
        if not all([self.master_url, self.instance_id, self.instance_key]):
            logger.error("❌ Missing required environment variables for Handshake.")
            return False

        payload = RegisterRequest(
            instance_id=self.instance_id,
            instance_key=self.instance_key,
            layer=os.getenv("LAYER", "EXTERNAL"),
            metadata={"os": os.name}
        )

        try:
            async with httpx.AsyncClient() as client:
                logger.info(f"Attempting Handshake with {self.master_url}...")
                resp = await client.post(
                    f"{self.master_url}/register", 
                    json=payload.model_dump()
                )
                
                if resp.status_code == 200:
                    data = RegisterResponse(**resp.json())
                    self.access_token = data.access_token
                    
                    # Persist Token
                    token_path = Path(__file__).parent.parent.parent / "token.json"
                    with open(token_path, "w", encoding="utf-8") as f:
                        json.dump({"access_token": self.access_token, "acquired_at": str(datetime.now())}, f)
                    
                    logger.info(f"Handshake Success. Token saved to {token_path}")
                    return True
                else:
                    logger.error(f"Handshake Refused: {resp.text}")
        except Exception as e:
            logger.error(f"❌ Handshake Error: {e}")
            
        return False

    def get_token(self):
        return self.access_token
