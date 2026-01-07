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
