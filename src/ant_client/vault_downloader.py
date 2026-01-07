import asyncio
import httpx
import os
import json
import base64
from typing import Dict, List, Optional
from src.ant_client.core.vault.shredder import VaultShredder
from src.common.erasure_coding import ErasureCoding
from src.ant_client.core.p2p.engine import P2PEngine
from src.core.ant_security import AntSecurity

class VaultDownloader:
    def __init__(self, api_url: str, api_key: str, p2p_engine: P2PEngine):
        self.api_url = api_url
        self.api_key = api_key
        self.p2p = p2p_engine
        
        # Hardcoded for Phase 6 (Must match Shredder)
        self.N = 10
        self.M = 4 # Parity
        self.rs = ErasureCoding(n=self.N, m=self.M) 
        
        # Buffer for incoming shards
        self.received_shards: Dict[int, bytes] = {}
        self._download_future: Optional[asyncio.Future] = None

    async def download_file(self, file_id: int, output_dir: str):
        """
        Orchestrates the full download flow.
        """
        print(f"📥 REQUESTING Download for File ID {file_id}...")
        
        # 1. Init Download with Queen
        async with httpx.AsyncClient() as client:
            headers = {"X-API-Key": self.api_key}
            init_data = {"file_id": file_id}
            
            resp = await client.post(f"{self.api_url}/api/v1/vault/manager/download/init", json=init_data, headers=headers)
            if resp.status_code != 200:
                print(f"❌ Download Init failed: {resp.text}")
                return None
            
            meta = resp.json()
            print(f"📄 Metadata Received: {meta['filename']} ({meta['file_size_bytes']} bytes)")
            
            shards_info = meta["shards"]
            encrypted_size = meta["encrypted_size_bytes"]
            key_hex = meta["encryption_key_hex"]
            
            # Setup Future to wait for enough shards
            self.received_shards = {}
            # We need at least N shards to recover (technically N data shards, but RS needs N total blocks usually)
            # Striped RS logic: Needs N shards to reconstruct.
            needed = self.N
            
            # 2. Request Shards
            print(f"📡 Requesting shards from swarm (Need {needed})...")
            
            for s in shards_info:
                idx = s["shard_index"]
                addr = s["ant_addr"]
                
                if not addr: 
                    continue
                    
                ip, port = addr.split("|")
                port = int(port)
                
                req_payload = {
                    "type": "request_shard",
                    "file_id": file_id,
                    "shard_index": idx
                }
                # 0x20 = GET_SHARD
                self.p2p.protocol.send_message(0x20, req_payload, (ip, port))
                
            # 3. Wait for Responses (with Timeout)
            # In a real app we'd attach a specific listener.
            # For this Phase 6, we assume the TEST SCRIPT pushes data into `received_shards`
            # or calls a method `on_shard_received`.
            
            # We wait loop
            try:
                for _ in range(50): # 5 seconds wait
                    if len(self.received_shards) >= needed:
                        break
                    await asyncio.sleep(0.1)
            except Exception as e:
                print(f"Wait error: {e}")
                
            if len(self.received_shards) < needed:
                print(f"❌ Failed to gather enough shards. Got {len(self.received_shards)}/{needed}")
                # return None # For test we might try anyway or fail
            
            print(f"✅ Collected {len(self.received_shards)} shards. Reassembling...")
            
            # 4. Reassemble & Decode
            # Reconstruct list for RS (None for missing)
            shards_list = []
            total_blocks = self.N + self.M
            
            for i in range(total_blocks):
                shards_list.append(self.received_shards.get(i)) # bytes or None
                
            try:
                # Use Striped RS decode
                recovered_enc_data = self.rs.decode(shards_list)
                # Truncate to original size (remove padding)
                if encrypted_size:
                    recovered_enc_data = recovered_enc_data[:encrypted_size]
            except Exception as e:
                print(f"❌ RS Decode Failed: {e}")
                return None
                
            # 5. Decrypt
            try:
                security = AntSecurity()
                # Use raw AES decrypt (AntSecurity uses defaults, need to ensure key/nonce match)
                # VaultShredder used standard AESGCM.
                from cryptography.hazmat.primitives.ciphers.aead import AESGCM
                
                aes = AESGCM(bytes.fromhex(key_hex))
                # Nonce is prepended? VaultShredder: nonce = os.urandom(12); return nonce + ciphertext
                nonce = recovered_enc_data[:12]
                ciphertext = recovered_enc_data[12:]
                
                original_data = aes.decrypt(nonce, ciphertext, None)
                
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                    
                output_file = os.path.join(output_dir, meta["filename"])
                with open(output_file, "wb") as f:
                    f.write(original_data)
                    
                print(f"✅ File saved to {output_file}")
                return output_file
                
            except Exception as e:
                print(f"❌ Decryption Failed: {e}")
                return None

    def on_shard_received(self, shard_index: int, data: bytes):
        """Callback for P2P Engine when a shard arrives"""
        print(f"📥 Received Shard #{shard_index} ({len(data)} bytes)")
        self.received_shards[shard_index] = data
