import asyncio
import websockets
import json
import random
import uuid
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.ant_security import AntSecurity

SERVER_URL = "ws://127.0.0.1:8000"
GPU_MODELS = ["RTX_3060", "RTX_3070", "RTX_3080", "RTX_3090", "RTX_4090", "A100_40GB"]

async def run_ant(client_id):
    """Simulates a single Ant Client."""
    gpu = random.choice(GPU_MODELS)
    url = f"{SERVER_URL}/ws/ant/{client_id}"
    security = AntSecurity() # Default key
    
    retry_delay = 1
    
    # [Phase 6 Update]
    import aiohttp

    while True:
        try:
            print(f"[{client_id}] Connecting... ({gpu})")
            # CORS: Some servers reject WS without Origin
            async with websockets.connect(url, additional_headers={"Origin": "http://localhost:3000"}) as ws:
                print(f"[{client_id}] Connected!")
                
                # Loop
                while True:
                    # Send Heartbeat
                    status = random.choice(["ONLINE", "ONLINE", "ONLINE", "WORKING"])
                    
                    payload = {
                        "type": "heartbeat",
                        "client_id": client_id,
                        "status": status,
                        "timestamp": 0 # Server ignores/overwrites for now or uses it
                    }
                    
                     # [Phase 6] Announce P2P Address to Tracker
                    # Each mock ant claims port 60000 + i (Assuming i is derivable or random)
                    # We can pick a random port for mock
                    p2p_port = 60000 + random.randint(1, 999)
                    
                    # For tracker API, we need a user session or key?
                    # Since Mockants are "Clients", they talk to Queen via HTTP API too.
                    # But they are "Ants", not "Users".
                    # Tracker API `/tracker/announce` requires `User` currently.
                    # THIS IS A DESIGN FLAW detected during Mock implementation.
                    # Ant Clients should authenticate via Client Certificate or distinct "Ant Token", not "User API Key".
                    # However, for simplicity in Phase 6, we might have used User Key.
                    # Let's check `tracker.py` -> `user: User = Depends(get_api_key_user)`.
                    # Does Ant have an API key? Not currently.
                    
                    # WORKAROUND for Demo:
                    # We will skip Announce in Mock script for now to avoid Auth error,
                    # OR we give a dummy key to Ants.
                    
                    # Decision: SKIP Announce in this Python script to avoid complexity.
                    # The Integration Test manually populates Redis, so Verification is safe.
                    # This Mock script is just for Dashboard Visuals.
                    
                    # Encrypt
                    encrypted = security.encrypt_payload(payload)
                    await ws.send(encrypted)
                    
                    # Recv Ack (or Job)
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=2.0)
                        # We ignore msg content for this mock, just keeping connection alive
                    except asyncio.TimeoutError:
                        pass
                        
                    await asyncio.sleep(3) # Heartbeat every 3s
                    
        except Exception as e:
            print(f"[{client_id}] Error: {e}")
            await asyncio.sleep(5)

async def main():
    num_ants = 10
    tasks = []
    print(f"🚀 Launching {num_ants} Mock Ants...")
    
    for i in range(num_ants):
        cid = f"ant-mock-{i:03d}"
        tasks.append(asyncio.create_task(run_ant(cid)))
        
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Stopping Mock Ants")
