import asyncio
import socket
import logging
from .protocol import P2PProtocol

logger = logging.getLogger("AntP2P")

class P2PEngine:
    def __init__(self, p2p_id: str, port: int = 0):
        self.p2p_id = p2p_id
        self.port = port
        self.protocol = None
        self.transport = None

    async def start(self):
        """
        Start UDP Server for P2P Transfer.
        Port 0 means random available port.
        """
        loop = asyncio.get_running_loop()
        
        # 0.0.0.0 binds to all interfaces
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: P2PProtocol(self),
            local_addr=('0.0.0.0', self.port)
        )
        
        self.transport = transport
        self.protocol = protocol
        
        # Get actual bound port
        sock = transport.get_extra_info('socket')
        self.port = sock.getsockname()[1]
        
        logger.info(f"🕸️ [DeepVault P2P] Engine Started on Port {self.port}")
        
        # TODO: Start periodic Announce to Queen Tracker

    async def connect_to_peer(self, ip: str, port: int):
        """
        UDP Hole Punching Initiator.
        Send 'Hello' to target peer.
        """
        logger.info(f"🥊 Punching Hole to {ip}:{port}")
        self.protocol.send_message(0x01, {"id": self.p2p_id}, (ip, port))

    def stop(self):
        if self.transport:
            self.transport.close()
