import asyncio
import websockets
import json
import logging
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.ant_security import AntSecurity
from src.ant_client.core.executor import JobExecutor
from src.core.protocol import JobRequest, JobType
from src.config import settings

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SmartAnt")

SERVER_URL = "ws://127.0.0.1:8000"

# Mock Vault Components for Demo
class MockVaultDownloader:
    async def download_file(self, file_id: int, dest_dir: str) -> str:
        logger.info(f"📥 [MockVault] Downloading file {file_id}...")
        # Return local cube.blend path
        # Assuming cube.blend is in project root
        file_path = os.path.join(settings.BASE_DIR, "cube.blend")
        if not os.path.exists(file_path):
             logger.warning(f"⚠️ cube.blend not found at {file_path}, creating dummy...")
             with open(file_path, "wb") as f:
                 f.write(b"DUMMY_BLEND_CONTENT")
        
        return file_path

class MockVaultUploader:
    async def upload_file(self, file_path: str) -> int:
        logger.info(f"📤 [MockVault] Uploading result {file_path}...")
        # In a real scenario, this uploads to Vault and returns ID.
        # For demo, we just return magic ID 777.
        return 777

async def run_smart_ant(client_id):
    url = f"{SERVER_URL}/ws/ant/{client_id}"
    security = AntSecurity()
    
    # Initialize Real Executor with Mock Vault
    executor = JobExecutor(
        client_id=client_id,
        vault_downloader=MockVaultDownloader(),
        vault_uploader=MockVaultUploader()
    )
    
    logger.info(f"🧠 Smart Ant {client_id} Connecting to Queen...")
    
    while True:
        try:
            async with websockets.connect(url) as ws:
                logger.info(f"🧠 {client_id} Connected!")
                
                while True:
                    # Heartbeat
                    payload = {"type": "heartbeat", "client_id": client_id, "status": "ONLINE"}
                    await ws.send(security.encrypt_payload(payload))
                    
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        data = json.loads(msg)
                        
                        if data.get("type") == "job_request":
                            logger.info(f"⚡ Received Job Request: {data}")
                            # Parse JobRequest using Pydantic
                            # data['data'] is the dict
                            job_data = data.get("data")
                            job = JobRequest(**job_data)
                            
                            # Execute using Real Logic (Blender)
                            result = await executor.execute_job(job)
                            
                            # Send Result
                            # Protocol expects dict
                            result_payload = {
                                "type": "job_result",
                                "client_id": client_id,
                                "data": result.dict()
                            }
                            await ws.send(security.encrypt_payload(result_payload))
                            logger.info(f"✅ Job {job.job_id} Result Sent")
                            
                    except asyncio.TimeoutError:
                        pass
                    except Exception as e:
                        logger.error(f"Processing Error: {e}")
                        
                    await asyncio.sleep(0.1)
                    
        except Exception as e:
            logger.error(f"Connection Error: {e}. Retrying in 5s...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    # Single Ant for Real Engine Test
    try:
        asyncio.run(run_smart_ant("ant-real-engine-01"))
    except KeyboardInterrupt:
        pass
