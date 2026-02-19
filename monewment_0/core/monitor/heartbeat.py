import asyncio
import os
import sys
import httpx
import logging
import psutil
from datetime import datetime

# sys.path injection to ensure absolute imports from EDENVALE/monewment_0 structure if shared
# But for an ANT, we assume local imports or relative to the spawned package
from dna.onboarding_package.protocol.fis_schema import HeartbeatMessage

logger = logging.getLogger("Heartbeat")

async def start_heartbeat(master_url: str, interval: int = 60):
    """
    [The Codex Pulse]
    Sends health reports to EDENVALE with Stratium/Queen/Ant context.
    """
    stratium = os.getenv("STRATIUM_ID", "UNKNOWN")
    queen = os.getenv("QUEEN_ID", "UNKNOWN")
    ant = os.getenv("ANT_ID", "UNKNOWN")
    
    logger.info(f"💓 Heartbeat started for {ant} ({queen}@{stratium})")
    
    # Edenvale Master API fixed endpoint
    endpoint = f"{master_url}/v1/heartbeat"
    
    while True:
        # Construct message with Codex metadata
        payload = {
            "stratium": stratium,
            "queen": queen,
            "ant": ant,
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(endpoint, json=payload, timeout=5.0)
                if resp.status_code != 200:
                    logger.warning(f"⚠️ Heartbeat rejected: {resp.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ Heartbeat failed to reach master: {e}")
            
        await asyncio.sleep(interval)

if __name__ == "__main__":
    # Test execution
    asyncio.run(start_heartbeat(os.getenv("MASTER_API", "http://127.0.0.1:8201")))
