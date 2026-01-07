import asyncio
import pytest
import os
import shutil
import base64
from unittest.mock import MagicMock, AsyncMock, patch
from src.ant_client.vault_uploader import VaultUploader
from src.ant_client.vault_downloader import VaultDownloader
from src.core.redis_client import RedisManager
from src.ant_client.core.p2p.engine import P2PEngine
from src.ant_client.core.vault.shredder import VaultShredder

API_URL = "http://127.0.0.1:8000"
API_KEY = "test_key_123"

# Mock P2P Engine to capture sends and simulate receives
class MockP2PEngine:
    def __init__(self):
        self.protocol = MagicMock()
        self.protocol.send_message = MagicMock()
        self.sent_packets = []
        
        # Capture sent packets
        def side_effect(msg_type, payload, addr):
            # print(f"  [MockP2P] Sent {hex(msg_type)} to {addr}")
            self.sent_packets.append((msg_type, payload, addr))
        self.protocol.send_message.side_effect = side_effect

@pytest.mark.asyncio
async def test_full_download_flow():
    print("\n🚀 Starting Vault Download Integration Test...")
    
    # Setup
    test_dir = "tests/temp_download_test"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    original_file = os.path.join(test_dir, "secret_doc.txt")
    with open(original_file, "wb") as f:
        f.write(b"DeepVault Top Secret Content " * 50) # 1350 bytes
        
    p2p_mock = MockP2PEngine()
    
    # 1. UPLOAD FIRST (To populate DB)
    uploader = VaultUploader(API_URL, API_KEY, p2p_mock)
    
    # We assume Manager is running (or we mock it? Manager is needed for DB state)
    # We will assume LIVE Manager for this test (Integration)
    # This requires `python main.py` to be running.
    # If not running, this test will fail. 
    # But usually "Integration" implies env. 
    # Since we can't ensure server is running in this interaction,
    # We will MOCK the UPLOAD response to just give us IDs,
    # AND MOCK the DOWNLOAD Init response.
    # Actually, let's try to hit the live server if available, else mock.
    # Given previous steps, `main.py` is NOT running in background unless I started it?
    # I have not started `main.py` in background.
    # So I MUST Mock the API calls or Use `TestClient`.
    
    # Pivot: Use `TestClient` for API interaction, and `MockP2P` for network.
    from src.main import app
    from fastapi.testclient import TestClient
    
    # We need to patch Redis in Main logic too if we want to bypass real Redis
    # But we want to test the full flow "logic".
    
    # It's better to verify "Downloader" class in isolation with Mocked API.
    
    print("🔧 Mocking API responses for Downloader...")
    
    # Prepare Mock Data
    file_id = 999
    key_hex = "00" * 32 # Dummy key
    # Create valid shards to simulate "Network"
    shredder = VaultShredder()
    meta = shredder.process_file(original_file)
    shards = meta["shards"]
    key_hex = meta["key"] # Real key from shredder
    
    # Mock Init Response
    mock_shards_info = []
    for i in range(len(shards)):
        mock_shards_info.append({
            "shard_index": i,
            "ant_id": f"ant_{i}",
            "ant_addr": f"127.0.0.1|{60000+i}",
            "shard_hash": "hash"
        })
        
    mock_init_resp = {
        "file_id": file_id,
        "filename": "secret_doc.txt",
        "file_hash": "hash",
        "file_size_bytes": meta["file_size"],
        "encrypted_size_bytes": meta["encrypted_size"],
        "encryption_key_hex": key_hex,
        "shards": mock_shards_info
    }
    
    downloader = VaultDownloader(API_URL, API_KEY, p2p_mock)
    
    # Patch httpx to return mock_init_resp
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_init_resp
        mock_post.return_value = mock_resp
        
        # Start Download in background task (it waits for shards)
        dl_task = asyncio.create_task(downloader.download_file(file_id, test_dir))
        
        # Allow it to run and send requests
        await asyncio.sleep(1)
        
        # Verify it sent requests
        assert len(p2p_mock.sent_packets) == len(shards)
        print("✅ Downloader requested all shards via P2P.")
        
        # Simulate Incoming Shards (Network Response)
        print("📡 Simulating Shard Arrival...")
        for i, data in enumerate(shards):
            # Inject data into downloader
            downloader.on_shard_received(i, data)
            
        # Wait for finish
        output_path = await dl_task
        
        assert output_path is not None
        assert os.path.exists(output_path)
        
        with open(output_path, "rb") as f:
            content = f.read()
            
        with open(original_file, "rb") as f:
            original = f.read()
            
        assert content == original
        print("✅ File Content Verified! Download success.")
        
    # Cleanup
    shutil.rmtree(test_dir)

if __name__ == "__main__":
    asyncio.run(test_full_download_flow())
