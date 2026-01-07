import asyncio
import pytest
import os
import shutil
import json
from unittest.mock import MagicMock, AsyncMock, patch
from src.ant_client.repair_agent import RepairAgent
from src.ant_client.core.p2p.engine import P2PEngine
from src.ant_client.core.vault.shredder import VaultShredder

API_URL = "http://127.0.0.1:8000"
API_KEY = "test_key_123"

class MockP2P(P2PEngine):
    def __init__(self):
        self.protocol = MagicMock()
        self.protocol.send_message = MagicMock()
        self.sent = []
        self.protocol.send_message.side_effect = lambda t, p, a: self.sent.append((t, p, a))

@pytest.mark.asyncio
async def test_repair_agent_flow():
    print("\n🚀 Starting Repair Agent Test...")
    
    # 1. Setup Mock Environment
    test_dir = "tests/temp_repair_test"
    if os.path.exists(test_dir): shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    p2p_mock = MockP2P()
    agent = RepairAgent(API_URL, API_KEY, p2p_mock)
    
    # Mock Downloader to return a "Recovered File" without actual network
    # We cheat here because download was tested separately in Phase 6-4.
    async def mock_download(fid, out_dir):
        path = os.path.join(out_dir, "repaired.txt")
        with open(path, "wb") as f:
            f.write(b"Recovered Content")
        return path
    agent.downloader.download_file = AsyncMock(side_effect=mock_download)
    
    # Mock HTTPX for Repair Init/Complete
    mock_repair_plan = {
        "file_id": 100,
        "assignments": [
            {"shard_index": 0, "target_ants": ["ant1"], "target_addrs": ["127.0.0.1|9000"]},
            {"shard_index": 1, "target_ants": ["ant2"], "target_addrs": ["127.0.0.1|9001"]}
        ]
    }
    
    # We patch httpx within agent.process_repair_job
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        # Define behavior for different endpoints
        def side_effect(url, json, headers):
            resp = MagicMock()
            resp.status_code = 200
            
            if "repair/init" in url:
                print("➡️ Repair Init Called")
                resp.json.return_value = mock_repair_plan
            elif "upload/complete" in url:
                print("➡️ Repair Complete Called")
                resp.json.return_value = {"status": "ok"}
                
            return resp
            
        mock_post.side_effect = side_effect
        
        # Trigger Repair Job
        job = {"file_id": 100, "filename": "test.txt", "key_hex": "00"*32}
        await agent.process_repair_job(job)
        
        # Verify
        assert len(p2p_mock.sent) == 2 # 2 shards in plan
        assert p2p_mock.sent[0][0] == 0x10 # STORE_SHARD
        print("✅ Repair Agent sent new shards.")
        
        # Verify complete called
        assert mock_post.call_count == 2
        
    print("✅ Repair Flow Verified.")
    shutil.rmtree(test_dir)

if __name__ == "__main__":
    asyncio.run(test_repair_agent_flow())
