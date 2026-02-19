import os
import json
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path

app = FastAPI(title="EDENVALE Master Registry")

VAULT_DIR = Path("C:/monewment/data/vault")
VAULT_DIR.mkdir(parents=True, exist_ok=True)

class CodexHeartbeat(BaseModel):
    stratium: str
    queen: str
    ant: str
    cpu_usage: float
    memory_usage: float
    timestamp: str

@app.get("/health")
def health():
    return {"status": "online", "mode": "Master API"}

@app.post("/v1/heartbeat")
async def receive_codex_heartbeat(message: CodexHeartbeat):
    """
    [The Codex Health Monitor]
    Logs heartbeat data into the central persistence vault.
    """
    log_file = VAULT_DIR / "heartbeats.jsonl"
    
    log_entry = message.model_dump()
    log_entry["received_at"] = datetime.now().isoformat()
    
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        print(f"[Vault] Sync: {message.ant} in {message.queen} (CPU: {message.cpu_usage}%)")
        return {"status": "SUCCESS", "vaulted": True}
    except Exception as e:
        print(f"!!! Vault Persistence Error: {e} !!!")
        raise HTTPException(status_code=500, detail="Vault failure")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8201)
