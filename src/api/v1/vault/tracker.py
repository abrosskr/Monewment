from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict
from pydantic import BaseModel
from src.core.redis_client import RedisManager
from src.core.security import get_api_key_user
from src.models import User

router = APIRouter()

class PeerAnnounce(BaseModel):
    file_ids: List[str]
    ip: str
    port: int
    p2p_id: str

class PeerInfo(BaseModel):
    p2p_id: str
    ip: str
    port: int

@router.post("/tracker/announce", summary="Announce Files to Tracker")
async def announce_files(
    data: PeerAnnounce,
    user: User = Depends(get_api_key_user)
):
    """
    [Ant -> Queen] I have these files.
    Redis Structure:
    1. `vault:file:{file_hash}` (Set) -> `{ip}|{port}|{p2p_id}`
    2. `vault:peer:{p2p_id}` -> timestamp (Heartbeat)
    """
    redis = RedisManager.get_instance().get_client()
    if not redis:
        raise HTTPException(503, "Tracker unavailable")

    pipeline = redis.pipeline()
    for file_hash in data.file_ids:
        # Peer info format: "1.2.3.4|12345|ant_node_1"
        value = f"{data.ip}|{data.port}|{data.p2p_id}"
        key = f"vault:file:{file_hash}"
        pipeline.sadd(key, value)
        pipeline.expire(key, 3600) # 1 hour TTL for simplicity

    # Update Peer Liveness AND Address Map
    # vault:node:{id} -> "ip|port"
    pipeline.set(f"vault:node:{data.p2p_id}", f"{data.ip}|{data.port}", ex=300)
    pipeline.set(f"vault:peer:{data.p2p_id}", "alive", ex=300) 
    
    await pipeline.execute()
    return {"status": "announced", "count": len(data.file_ids)}

@router.get("/tracker/peers/{file_hash}", response_model=List[PeerInfo], summary="Find Peers")
async def find_peers(
    file_hash: str,
    user: User = Depends(get_api_key_user)
):
    """
    [Ant -> Queen] Who has this file?
    """
    redis = RedisManager.get_instance().get_client()
    if not redis:
        raise HTTPException(503, "Tracker unavailable")

    key = f"vault:file:{file_hash}"
    members = await redis.smembers(key)
    
    peers = []
    for member in members:
        # Decode "ip|port|id"
        try:
            m_str = member.decode()
            ip, port, pid = m_str.split('|')
            peers.append(PeerInfo(ip=ip, port=int(port), p2p_id=pid))
        except:
            continue
            
    return peers
