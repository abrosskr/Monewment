from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
import json
import asyncio
from datetime import datetime, timedelta
from src.core.redis_client import RedisManager
from src.dependencies import get_db

router = APIRouter()

@router.get("/status")
async def get_grid_status():
    """
    Get aggregate status of the DeepSync Grid.
    Returns: Total Ants, Active Ants, Total TFLOPS, Current Revenue Rate
    """
    redis = RedisManager.get_instance().get_client()
    if not redis:
        return {"status": "error", "message": "Redis not available"}

    # 1. Get all heartbeats to count online ants
    # Pattern: ant:heartbeat:{client_id}
    keys = await redis.keys("ant:heartbeat:*")
    total_ants = len(keys)
    
    active_ants = 0
    total_tflops = 0.0
    current_revenue_per_hr = 0.0
    
    # 2. Get detailed info for stats
    # Pattern: ant:info:{client_id} -> JSON
    # Optimization: Use pipeline or mget if keys are predictable, but here we scan.
    # We extracted client_ids from heartbeat keys.
    client_ids = [k.split(":")[-1] for k in keys]
    
    if client_ids:
        info_keys = [f"ant:info:{cid}" for cid in client_ids]
        infos = await redis.mget(info_keys)
        
        from src.core.billing.profit_engine import HARDWARE_SPECS, GpuType, ProfitEngine, ProfitCalculationRequest
        
        for info_json in infos:
            if not info_json:
                continue
            
            try:
                data = json.loads(info_json)
                status = data.get("status", "OFFLINE")
                gpu_model = data.get("gpu", "RTX_3060") # Default
                
                if status in ["WORKING", "ONLINE", "IDLE"]: 
                    active_ants += 1
                
                # Calculate TFLOPS
                spec = HARDWARE_SPECS.get(gpu_model)
                if not spec:
                     # Try Enum
                     try: spec = HARDWARE_SPECS.get(GpuType(gpu_model))
                     except: pass
                
                if spec:
                    total_tflops += spec.tflops
                    
                    # Calculate Revenue (Approx)
                    # Assuming full utilization for online nodes for metric "Capacity"
                    # Or current utilization for "Current Revenue"
                    
                    # Let's show "Capacity Revenue" for now
                    req = ProfitCalculationRequest(
                         gpu_type=GpuType(gpu_model) if spec else GpuType.RTX_3060,
                         electricity_cost_per_kwh=0.12,
                         active_hours_per_day=24,
                         deep_sync_utilization=1.0,
                         deep_render_utilization=0.0
                    )
                    res = ProfitEngine.calculate_profit(req)
                    # daily / 24 = hourly
                    current_revenue_per_hr += float(res.daily_revenue) / 24.0
                    
            except Exception as e:
                import logging
                logging.getLogger("Monitoring").error(f"Error processing Ant {cid} stats: {e}")
                continue

    return {
        "total_nodes": total_ants,
        "working_nodes": active_ants,
        "total_tflops": round(total_tflops, 2),
        "revenue_per_hour": round(current_revenue_per_hr, 4),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/list")
async def get_ant_list():
    """
    Get list of all connected Ants with details.
    """
    redis = RedisManager.get_instance().get_client()
    if not redis:
        return []
        
    keys = await redis.keys("ant:heartbeat:*")
    client_ids = [k.split(":")[-1] for k in keys]
    
    if not client_ids:
        return []
        
    info_keys = [f"ant:info:{cid}" for cid in client_ids]
    infos = await redis.mget(info_keys)
    
    result = []
    
    # We might want last_seen from heartbeat key TTL or value
    # Heartbeat value is timestamp
    heartbeat_vals = await redis.mget(keys)
    
    for cid, info_json, hb_val in zip(client_ids, infos, heartbeat_vals):
        ant_data = {
            "id": cid,
            "status": "UNKNOWN",
            "gpu": "Unknown",
            "last_seen": hb_val if hb_val else None,
            "ip": "127.0.0.*" # Mock masking
        }
        
        if info_json:
            try:
                data = json.loads(info_json)
                ant_data.update(data)
            except:
                pass
        
        result.append(ant_data)
        
    return result

@router.post("/sync_token")
async def sync_ant_token(data: Dict[str, str]):
    """
    [Phase 10] Hand over a JWT token from Web UI to the target Ant Client.
    Called by the dashboard upon successful login in Client Context.
    """
    client_id = data.get("client_id")
    token = data.get("token")
    
    if not client_id or not token:
        raise HTTPException(status_code=400, detail="client_id and token are required")

    redis = RedisManager.get_instance().get_client()
    if not redis:
        raise HTTPException(status_code=503, detail="Redis unavailable")

    # 1. Store in Redis for recovery/silent-start
    await redis.set(f"ant:token:{client_id}", token, ex=3600*24*7) # 7 Days

    # 2. Immediate push to active worker via WebSocket
    from src.core.socket_manager import SocketManager
    manager = SocketManager.get_instance()
    
    if manager.get_connection(client_id):
        try:
            payload = {"type": "token_sync", "token": token}
            await manager.send_message(client_id, json.dumps(payload))
            return {"status": "success", "message": "Token pushed to active worker."}
        except Exception as e:
            return {"status": "partial_success", "message": f"Token saved but push failed: {e}"}
    
    return {"status": "success", "message": "Token saved. Worker will fetch on next connect."}
