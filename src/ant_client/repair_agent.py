import asyncio
import os
import shutil
import base64
import json
import logging
from src.ant_client.vault_downloader import VaultDownloader
from src.ant_client.vault_uploader import VaultUploader
from src.ant_client.core.p2p.engine import P2PEngine
import httpx

logger = logging.getLogger("RepairAgent")

class RepairAgent:
    def __init__(self, api_url: str, api_key: str, p2p_engine: P2PEngine):
        self.api_url = api_url
        self.api_key = api_key
        self.p2p = p2p_engine
        self.downloader = VaultDownloader(api_url, api_key, p2p_engine)
        self.uploader = VaultUploader(api_url, api_key, p2p_engine)
        
    async def process_repair_job(self, job_data: dict):
        file_id = job_data.get("file_id")
        filename = job_data.get("filename", f"repair_{file_id}.tmp")
        
        logger.info(f"🔧 Starting Repair for File {file_id}...")
        
        # Temp dir
        temp_dir = f"temp_repair_{file_id}"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
        try:
            # 1. Recover (Download)
            # Downloader returns the path to the decrypted file
            local_path = await self.downloader.download_file(file_id, temp_dir)
            
            if not local_path or not os.path.exists(local_path):
                logger.error(f"❌ Repair Failed: Could not recover file {file_id}")
                return
                
            logger.info("✅ File Recovered. Resharding...")
            
            # 2. Reshard & Re-Upload
            # We use Uploader logic but need to override INIT step to "Repair Init"
            # Since VaultUploader is tightly coupled, we will manually orchestrate here to reuse its Shredder
            
            # Shred
            meta = self.uploader.shredder.process_file(local_path)
            shards = meta["shards"]
            key = meta["key"] # Note: This might generate a NEW key if random nonce used!
            # If we change the key, we must update Queen.
            # `complete_repair` accepts key update.
            
            # Init Repair
            async with httpx.AsyncClient() as client:
                headers = {"X-API-Key": self.api_key}
                resp = await client.post(
                    f"{self.api_url}/api/v1/vault/manager/repair/init", 
                    json={"file_id": file_id}, 
                    headers=headers
                )
                
                if resp.status_code != 200:
                    logger.error(f"❌ Repair Init Failed: {resp.text}")
                    return
                    
                plan = resp.json()
                assignments = plan["assignments"]
                
                # Distribute Shards
                # Reuse code or copy from Uploader?
                # Copying is safer for now to avoid refactoring Uploader.
                
                shard_reports = []
                
                for item in assignments:
                    idx = item["shard_index"]
                    target_addrs = item.get("target_addrs", [])
                    if not target_addrs: continue
                    
                    # Target info
                    ip, port = target_addrs[0].split("|")
                    port = int(port)
                    target_id = item["target_ants"][0]
                    
                    if idx >= len(shards):
                         logger.warning(f"Assignment index {idx} out of range (shards: {len(shards)})")
                         continue

                    shard_data = shards[idx]
                    
                    # Send
                    payload = {
                        "type": "store_shard",
                        "file_id": file_id,
                        "shard_index": idx,
                        "data_b64": base64.b64encode(shard_data).decode()
                    }
                    self.p2p.protocol.send_message(0x10, payload, (ip, port))
                    
                    # Prepare Report (Assume success for UDP/MVP)
                    # We need hash of shard for report
                    import hashlib
                    s_hash = hashlib.sha256(shard_data).hexdigest()
                    
                    shard_reports.append({
                        "shard_index": idx,
                        "ant_id": target_id,
                        "shard_hash": s_hash
                    })
                    
                logger.info(f"📡 Redistributed {len(shards)} shards.")
                
                # Complete Repair
                comp_req = {
                    "file_id": file_id,
                    "file_hash": meta.get("file_hash", "repaired_hash"), # Shredder doesn't return file hash?
                    "encryption_key_hex": key,
                    "shard_reports": shard_reports
                }
                # Fix: `complete_upload` needs file_hash. Shredder v1 didn't return it. 
                # Calculating hash manually.
                with open(local_path, "rb") as f:
                    file_content = f.read()
                    comp_req["file_hash"] = hashlib.sha256(file_content).hexdigest()

                resp = await client.post(
                    f"{self.api_url}/api/v1/vault/manager/upload/complete", 
                    json=comp_req, 
                    headers=headers
                )
                
                if resp.status_code == 200:
                    logger.info("✅ Repair Completed Successfully!")
                else:
                    logger.error(f"❌ Repair Complete Failed: {resp.text}")
                
        except Exception as e:
            logger.error(f"Repair Exception: {e}")
            
        finally:
            shutil.rmtree(temp_dir)
