import asyncio
import os
import sys
import hashlib
from aiohttp import web

# Import Updater
sys.path.append(os.getcwd())
from src.ant_client.core.updater import AntUpdater, logger

# Mock Server Logic
async def handle_version(request):
    host = request.headers.get("Host", "127.0.0.1:8081")
    return web.json_response({
        "version": "1.1.0",
        "download_url": f"http://{host}/update.bin",
        "hash": request.app["expected_hash"]
    })

async def handle_download(request):
    return web.Response(body=request.app["update_binary"])

async def start_mock_server(app, port):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', port)
    await site.start()
    return runner

async def test_updater():
    print("🛠️ Setup Mock Environment...")
    base_dir = "temp_test_updater"
    os.makedirs(base_dir, exist_ok=True)
    
    current_exe = os.path.join(base_dir, "client.exe")
    with open(current_exe, "wb") as f:
        f.write(b"OLD_VERSION_Bytes")
        
    update_bin = b"NEW_VERSION_Bytes_Verified"
    bin_hash = hashlib.sha256(update_bin).hexdigest()
    
    # Setup Mock Server
    app = web.Application()
    app.router.add_get('/api/client/version', handle_version)
    app.router.add_get('/update.bin', handle_download)
    app["update_binary"] = update_bin
    
    # ---------------------------------------------------------
    # Test 1: Hash Mismatch (Security Trap)
    # ---------------------------------------------------------
    print("\n[Test 1] Simulating Hash Mismatch (Man-in-the-Middle)...")
    app["expected_hash"] = "bad_hash_12345" # Wrong hash
    
    srv = await start_mock_server(app, 8081)
    
    updater = AntUpdater("1.0.0", "http://127.0.0.1:8081")
    updater.exe_path = current_exe # Injection
    
    update_data = await updater.check_for_updates()
    if update_data:
        success = await updater.perform_update(update_data)
        if not success and os.path.exists(current_exe):
            print("✅ SUCCESS: Updater rejected bad hash and preserved current.exe.")
        else:
            print("❌ FAILURE: Updater accepted bad hash or deleted file.")
    
    await srv.cleanup()
    
    # ---------------------------------------------------------
    # Test 2: Valid Update (Golden Path)
    # ---------------------------------------------------------
    print("\n[Test 2] Simulating Valid Update...")
    
    # Create NEW Application for Test 2 to avoid deprecated state change
    app2 = web.Application()
    app2.router.add_get('/api/client/version', handle_version)
    app2.router.add_get('/update.bin', handle_download)
    app2["update_binary"] = update_bin
    app2["expected_hash"] = bin_hash # Correct hash

    srv2 = await start_mock_server(app2, 8082)
    updater = AntUpdater("1.0.0", "http://127.0.0.1:8082")
    updater.exe_path = current_exe 
    
    # Reset file state
    if os.path.exists(current_exe + ".bak"): os.remove(current_exe + ".bak")
    with open(current_exe, "wb") as f: f.write(b"OLD_VERSION_Bytes")

    update_data = await updater.check_for_updates()
    try:
        # Mock subprocess.Popen to avoid actually running garbage bytes
        import subprocess
        original_popen = subprocess.Popen
        subprocess.Popen = lambda *args, **kwargs: print("   [Mock] Restart Triggered")
        
        # We expect SystemExit(0) on success
        try:
            await updater.perform_update(update_data)
        except SystemExit:
            pass # Expected
            
        # Verify Swap
        with open(current_exe, "rb") as f:
            content = f.read()
            if content == update_bin:
                print("✅ SUCCESS: Binary swapped correctly.")
            else:
                print("❌ FAILURE: Binary not swapped.")
                
        # Verify Backup
        if os.path.exists(current_exe + ".bak"):
            print("✅ SUCCESS: Backup created.")
        else:
             print("❌ FAILURE: No backup found.")
             
    finally:
        subprocess.Popen = original_popen
        await srv.cleanup()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_updater())
