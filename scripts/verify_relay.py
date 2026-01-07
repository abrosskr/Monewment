# Imports
import sys
import os
import asyncio
import websockets
import json
sys.path.append(os.getcwd())
from src.core.ant_security import AntSecurity

# Configuration
SERVER_URL = "ws://127.0.0.1:8000/ws/ant"
ALICE_ID = "alice_ant"
BOB_ID = "bob_ant"

# Security (Match server dummy key if any, or use default)
# Server main.py uses default AntSecurity() which loads key from env or hardcoded default.
security = AntSecurity()

async def run_client(client_id, target_id=None, is_sender=False):
    uri = f"{SERVER_URL}/{client_id}"
    print(f"🐜 [{client_id}] Connecting {uri}...")
    
    async with websockets.connect(uri) as websocket:
        print(f"✅ [{client_id}] Connected.")
        
        # Handshake / Auth (Enforced by Server)
        hb = {
            "type": "heartbeat",
            "client_id": client_id,
            "status": "ONLINE",
            "active_job_id": None,
            "timestamp": 1234567890
        }
        await websocket.send(security.encrypt_payload(hb))
        
        if is_sender:
            await asyncio.sleep(2) # Wait for Bob to connect
            print(f"📤 [{client_id}] Sending Relay Message to {target_id}...")
            
            payload = "This is a SECRET payload from Alice"
            msg = {
                "type": "RELAY",
                "client_id": client_id, # Server checks this?
                "target_id": target_id,
                "payload": payload
            }
            # Server decrypts, then checks type="RELAY"
            await websocket.send(security.encrypt_payload(msg))
            print(f"🚀 [{client_id}] Sent.")
            await asyncio.sleep(2) # Wait for delivery
            
        else:
            print(f"👂 [{client_id}] Listening...")
            try:
                # Wait for message with timeout
                # It might be Ack first, then Relay
                while True:
                    response_enc = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    # Server sends plain JSON responses usually (error/ack/relay)??
                    # main.py sends: json.dumps({"type": "ack", ...}) -> PLAIN text
                    # RELAY message in main.py: json.dumps(relay_msg) -> PLAIN text wrapper
                    
                    data = json.loads(response_enc)
                    print(f"📥 [{client_id}] Received: {data}")
                    
                    if data.get("type") == "RELAY":
                         # Relay Payload is matched
                         if data.get("payload") == "This is a SECRET payload from Alice":
                            print(f"✅ [{client_id}] SUCCESS: Relay received correctly!")
                            return True
                         else:
                            print(f"⚠️ [{client_id}] Payload mismatch.")
                            
                    if data.get("type") == "error":
                        print(f"❌ Error from Server: {data}")
                        return False
                        
            except asyncio.TimeoutError:
                print(f"❌ [{client_id}] Timeout! No RELAY message received.")
                return False

async def main():
    # Run Bob (Receiver) and Alice (Sender) concurrently
    conn_bob = run_client(BOB_ID, is_sender=False)
    conn_alice = run_client(ALICE_ID, target_id=BOB_ID, is_sender=True)
    
    results = await asyncio.gather(conn_bob, conn_alice)
    
    # Check Bob's result
    if results[0] is True:
        print("🎉 RELAY SYSTEM VERIFIED!")
    else:
        print("💥 RELAY SYSTEM FAILED.")

if __name__ == "__main__":
    asyncio.run(main())
