import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock, patch
from src.main import app
from src.dependencies import get_db
from src.core.security import get_api_key_user
from src.models import User, VaultFile
from src.core.redis_client import RedisManager

# Mock User
mock_user = User(id=1, email="test@test.com", api_key="secret", role="USER")

async def override_get_api_key_user():
    return mock_user

# Mock DB Session
mock_session = AsyncMock()
mock_session.commit = AsyncMock()
# mock_session.refresh = AsyncMock() # We need side effect
mock_session.add = MagicMock()
mock_session.execute = AsyncMock()

async def mock_refresh_side_effect(obj):
    obj.id = 123
mock_session.refresh.side_effect = mock_refresh_side_effect

async def override_get_db():
    yield mock_session

# Apply Overrides
app.dependency_overrides[get_api_key_user] = override_get_api_key_user
app.dependency_overrides[get_db] = override_get_db

@patch("src.main.engine")
@patch("src.core.redis_client.RedisManager.get_instance")
@patch("src.core.cluster_manager.ClusterManager.get_instance")
def test_init_upload(mock_cluster_manager, mock_redis_manager, mock_engine):
    # Mock Cluster Manager
    mock_cluster_manager.return_value.initialize = AsyncMock()

    # Mock Engine for Lifespan
    mock_connection = AsyncMock()
    mock_engine.begin.return_value.__aenter__.return_value = mock_connection
    
    # Configure Startup Mock
    mock_instance = mock_redis_manager.return_value
    mock_instance.connect = AsyncMock()
    mock_instance.close = AsyncMock() # Fix shutdown error
    
    # Mock Redis Client Logic
    mock_redis = AsyncMock()
    mock_redis.keys.return_value = [b"ant:heartbeat:ant1", b"ant:heartbeat:ant2"]
    mock_redis.mget.return_value = [b"127.0.0.1|8001", b"127.0.0.1|8002"]
    
    mock_instance.get_client.return_value = mock_redis
    
    payload = {
        "filename": "top_secret.txt",
        "file_size_bytes": 1024,
        "encrypted_size_bytes": 1048,
        "shard_count": 4
    }
    
    # Use context manager to trigger startup with mocks in place
    with TestClient(app) as client:
        response = client.post("/api/v1/vault/manager/upload/init", json=payload, headers={"X-API-Key": "secret"})
        
        assert response.status_code == 200
        data = response.json()
        assert "file_id" in data
        assert len(data["assignments"]) == 4
        assert data["assignments"][0]["target_ants"][0] in ["ant1", "ant2"]
        print("\n✅ Init Upload Test Passed")

@patch("src.main.engine")
@patch("src.core.redis_client.RedisManager.get_instance")
@patch("src.core.cluster_manager.ClusterManager.get_instance")
def test_complete_upload(mock_cluster_manager, mock_redis_manager, mock_engine):
    # Mock Cluster Manager
    mock_cluster_manager.return_value.initialize = AsyncMock()

    # Mock Engine for Lifespan
    mock_connection = AsyncMock()
    mock_engine.begin.return_value.__aenter__.return_value = mock_connection

    # Configure Startup Mock
    mock_instance = mock_redis_manager.return_value
    mock_instance.connect = AsyncMock()
    mock_instance.close = AsyncMock()
    
    # Setup Mock DB to return a file
    mock_file = VaultFile(id=1, owner_id=1, status="UPLOADING")
    mock_result = MagicMock()
    mock_result.scalars().first.return_value = mock_file
    mock_session.execute.return_value = mock_result
    
    payload = {
        "file_id": 1,
        "file_hash": "final_hash_123",
        "encryption_key_hex": "key_hex_val"
    }
    
    with TestClient(app) as client:
        response = client.post("/api/v1/vault/manager/upload/complete", json=payload, headers={"X-API-Key": "secret"})
        
        assert response.status_code == 200
        assert mock_file.status == "AVAILABLE"
        assert mock_file.file_hash == "final_hash_123"
        print("\n✅ Complete Upload Test Passed")
