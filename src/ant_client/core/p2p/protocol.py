import asyncio
import json
import struct
from typing import Dict, Tuple, Optional

# Protocol Constants
MAGIC = b'ANT1'  # 4 bytes
TYPE_HELLO = 0x01
TYPE_ACK = 0x02
TYPE_REQUEST_CHUNK = 0x03
TYPE_DATA_CHUNK = 0x04

class P2PProtocol(asyncio.DatagramProtocol):
    def __init__(self, engine):
        self.engine = engine
        self.transport = None
        self.peer_map = {}  # { (ip, port): p2p_id }
        self.relay_transport = None

    def connection_made(self, transport):
        self.transport = transport
        print("[P2P] Listening on UDP")

    def datagram_received(self, data: bytes, addr: Tuple[str, int]):
        """
        Packet Format: [MAGIC(4)] [TYPE(1)] [PAYLOAD_LEN(4)] [PAYLOAD(N)]
        """
        if len(data) < 9:
            return

        magic, msg_type, length = struct.unpack("!4sBI", data[:9])
        if magic != MAGIC:
            return

        payload = data[9:9+length]
        
        asyncio.create_task(self.handle_packet(msg_type, payload, addr))

    async def handle_packet(self, msg_type, payload, addr):
        try:
            if msg_type == TYPE_HELLO:
                info = json.loads(payload.decode())
                print(f"[P2P] Hello from {info['id']} ({addr})")
                self.peer_map[addr] = info['id']
                # Send Ack
                self.send_message(TYPE_ACK, {"status": "ok"}, addr)
                
            elif msg_type == TYPE_REQUEST_CHUNK:
                req = json.loads(payload.decode())
                # TODO: Retrieve Chunk and Send
                pass
                
        except Exception as e:
            print(f"[P2P] Packet Error: {e}")

    def send_message(self, msg_type: int, data: Dict, addr: Tuple[str, int]):
        payload = json.dumps(data).encode('utf-8')
        header = struct.pack("!4sBI", MAGIC, msg_type, len(payload))
        self.transport.sendto(header + payload, addr)

    # ==========================
    # Relay Extension (NAT Traversal)
    # ==========================
    def set_relay_transport(self, callback):
        self.relay_transport = callback

    async def send_via_relay(self, msg_type: int, data: Dict, target_id: str):
        """Sends packet via Queen Relay (Base64 Encoded)."""
        if not self.relay_transport:
            return False
            
        payload = json.dumps(data).encode('utf-8')
        packet = struct.pack("!4sBI", MAGIC, msg_type, len(payload)) + payload
        
        # Encode to string for JSON transport
        import base64
        b64_packet = base64.b64encode(packet).decode()
        
        await self.relay_transport(target_id, b64_packet)
        return True

    async def handle_relayed_packet(self, sender_id: str, b64_packet: str):
        """Process packet received via Queen Relay."""
        import base64
        try:
            data = base64.b64decode(b64_packet)
            # Treat sender_id as the 'address' for map purposes
            # We map ('RELAY', sender_id) -> sender_id
            addr = ('RELAY', sender_id)
            
            # Reuse existing logic
            # To do this clean, we manually invoke the logic of datagram_received
            # but bypassing the magic check if we trust relay (we should still check)
            
            if len(data) < 9: return
            magic, msg_type, length = struct.unpack("!4sBI", data[:9])
            if magic != MAGIC: return
            
            payload = data[9:9+length]
            await self.handle_packet(msg_type, payload, addr)
            
        except Exception as e:
            print(f"[P2P] Relay Packet Error: {e}")
