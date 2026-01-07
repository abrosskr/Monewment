from fastapi import WebSocket
from typing import Dict, Optional
import asyncio
import structlog

logger = structlog.get_logger()

class SocketManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SocketManager, cls).__new__(cls)
            cls._instance.active_connections: Dict[str, WebSocket] = {}
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls()
        return cls._instance

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info("websocket_connected", client_id=client_id)

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info("websocket_disconnected", client_id=client_id)

    def get_connection(self, client_id: str) -> Optional[WebSocket]:
        return self.active_connections.get(client_id)

    async def send_message(self, client_id: str, message: str) -> bool:
        socket = self.active_connections.get(client_id)
        if socket:
            try:
                await socket.send_text(message)
                return True
            except Exception as e:
                logger.error("send_message_failed", client_id=client_id, error=str(e))
                self.disconnect(client_id)
        return False
