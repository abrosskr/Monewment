import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.core.logger import setup_logger
from src.core.redis_client import RedisManager
from src.core.socket_manager import SocketManager
from src.core.ant_security import AntSecurity
from src.api.v1.render.router import JobDatabase
from src.core.protocol import JobResult

logger = setup_logger()
router = APIRouter()

@router.websocket("/{client_id}")
async def ant_websocket_endpoint(websocket: WebSocket, client_id: str):
    manager = SocketManager.get_instance()
    await manager.connect(client_id, websocket)
    
    # [Phase 10] Push existing token from Redis if available (Silent Start support)
    try:
        redis = RedisManager.get_instance().get_client()
        token = await redis.get(f"ant:token:{client_id}")
        if token:
            logger.info(f"✨ Pushing cached token to {client_id}")
            await manager.send_message(client_id, json.dumps({"type": "token_sync", "token": token}))
    except Exception as e:
        logger.error(f"Failed to push initial token to {client_id}: {e}")

    # [Security] Initialize Decryptor
    security = AntSecurity() 
    
    try:
        while True:
            # Client sends encrypted token: "v1|nonce|ciphertext"
            encrypted_data = await websocket.receive_text()
            
            try:
                payload = security.decrypt_payload(encrypted_data)
                
                # Validate Payload
                if payload.get("client_id") != client_id:
                    logger.warning(f"⚠️ Security Alert: Client ID Mismatch")
                    await websocket.close(code=4003)
                    return
                    
                msg_type = payload.get("type")
                
                if msg_type == "job_result":
                    data = payload.get("data")
                    logger.info(f"🎨 Job Completed: {data.get('job_id')} by {client_id}")
                    
                    try:
                        res = JobResult(**data)
                        JobDatabase.add_result(res)
                    except Exception as e:
                        logger.error(f"Failed to parse JobResult: {e}")
                        
            except Exception as e:
                logger.error(f"Socket Payload Error: {e}")
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        # await manager.broadcast(f"Ant {client_id} disconnected.")
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")
        manager.disconnect(client_id)
