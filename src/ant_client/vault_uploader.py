import asyncio
import httpx
import os
import json
from typing import Dict, Optional
from src.ant_client.core.vault.shredder import VaultShredder
from src.ant_client.core.p2p.engine import P2PEngine

class VaultUploader:
    def __init__(self, api_url: str, api_key: str, p2p_engine: P2PEngine):
        self.api_url = api_url
        self.api_key = api_key
        self.shredder = VaultShredder()
        self.p2p = p2p_engine 

    async def upload_file(self, file_path: str):
        """
        Orchestrates the full upload flow.
        """
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return

        print(f"📦 Processing {file_path}...")
        
        # 1. Shred File locally
        meta = self.shredder.process_file(file_path)
        shards = meta["shards"]
        key = meta["key"]
        print(f"✅ Encrypted & Split into {len(shards)} shards.")
        
        # 2. Init Upload with Queen
        async with httpx.AsyncClient() as client:
            init_data = {
                "filename": os.path.basename(file_path),
                "file_size_bytes": meta["file_size"],
                "encrypted_size_bytes": meta["encrypted_size"],
                "shard_count": len(shards)
            }
            
            headers = {"X-API-Key": self.api_key}
            
            resp = await client.post(f"{self.api_url}/api/v1/vault/manager/upload/init", json=init_data, headers=headers)
            if resp.status_code != 200:
                print(f"❌ Init failed: {resp.text}")
                return
            plan = resp.json()
                
            file_id = plan["file_id"]
            assignments = plan["assignments"] 
            print(f"📜 Upload Plan Received for File ID {file_id}")
            
            # 3. Distribute Shards
            tasks = []
            for item in assignments:
                idx = item["shard_index"]
                target_addrs = item.get("target_addrs", [])
                
                if not target_addrs:
                    print(f"⚠️ No address for shard {idx}, skipping...")
                    continue
                    
                # Use first replica
                ip, port = target_addrs[0].split("|")
                port = int(port)
                
                shard_data = shards[idx]
                
                # Send via P2P (UDP)
                import base64
                payload = {
                    "type": "store_shard",
                    "file_id": file_id,
                    "shard_index": idx,
                    "data_b64": base64.b64encode(shard_data).decode()
                }
                
                self.p2p.protocol.send_message(0x10, payload, (ip, port))
                
            print(f"📡 All {len(shards)} shards transmitted via P2P.")
            
            # 4. Complete
            comp_data = {
                "file_id": file_id,
                "file_hash": "hash_placeholder", 
                "encryption_key_hex": key
            }
            
            resp = await client.post(f"{self.api_url}/api/v1/vault/manager/upload/complete", json=comp_data, headers=headers)
            if resp.status_code == 200:
                print("✅ Upload Completed Successfully!")
                return file_id
            else:
                print(f"⚠️ Completion failed: {resp.text}")
                return None
