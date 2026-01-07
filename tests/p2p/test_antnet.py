import asyncio
import logging
from src.ant_client.core.p2p.engine import P2PEngine

# Configure Logging
logging.basicConfig(level=logging.INFO)

async def test_p2p_handshake():
    print("🚀 Starting P2P Handshake Test...")
    
    # 1. Start Node A
    node_a = P2PEngine(p2p_id="ant_A")
    await node_a.start()
    print(f"✅ Node A started on port {node_a.port}")
    
    # 2. Start Node B
    node_b = P2PEngine(p2p_id="ant_B")
    await node_b.start()
    print(f"✅ Node B started on port {node_b.port}")
    
    # 3. A connects to B
    print(f"🔄 Node A connecting to Node B (127.0.0.1:{node_b.port})...")
    await node_a.connect_to_peer("127.0.0.1", node_b.port)
    
    # 4. Wait for Ack (Simulation)
    await asyncio.sleep(2)
    
    # 5. Check if B received Hello (Check internal map)
    # Note: In real test we would assert, here we just print internal state
    peers_b = node_b.protocol.peer_map
    print(f"📋 Node B's Peer List: {peers_b}")
    
    if any(pid == "ant_A" for pid in peers_b.values()):
         print("✅ SUCCESS: Node B sees Node A!")
    else:
         print("❌ FAILURE: Node A not found in Node B's list.")
         
    node_a.stop()
    node_b.stop()

if __name__ == "__main__":
    asyncio.run(test_p2p_handshake())
