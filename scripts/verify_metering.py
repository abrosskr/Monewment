
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import requests
import time
import json

BASE_URL = "http://localhost:8001"

def log(msg):
    print(f"[TEST] {msg}")

def run_test():
    # 1. Signup / Login (Simulated setup)
    # We will assume DB has initial data or we create it.
    # Let's create a project via API if possible, or just hack it if legacy.
    # Actually, create_vm requires project_id.
    
    # Create User
    user_email = f"metering_test_{int(time.time())}@test.com"
    r = requests.post(f"{BASE_URL}/api/auth/signup", json={
        "email": user_email, "password": "password", "name": "Tester"
    })
    if r.status_code == 200:
        user_id = r.json().get("user_id")
    else:
        # Maybe already exists
        log("User creation failed or exists, trying login...")
        r = requests.post(f"{BASE_URL}/api/auth/login", json={"email": user_email, "password": "password"})
        user_id = r.json().get("user_id")

    log(f"User ID: {user_id}")

    # Create Project
    project_name = f"metering_proj_{int(time.time())}"
    r = requests.post(f"{BASE_URL}/api/projects/create", json={
        "user_id": user_id, "project_name": project_name, "organization_name": "MeteringOrg"
    })
    log(f"Create Project: {r.status_code}")
    
    # We need project_id. The API returns status success but no ID? 
    # Let's verify DB or just assume project_id=1 if strictly sequential, but dangerous.
    # Let's fetch project list? 
    # The /projects endpoint returns folders.
    # We need the SQL ID.
    # Hack: Let's assume we can fetch it via direct DB access in this script if we use sqlalchemy.
    # Or update list_projects to return metadata.
    # For now, let's use the DB directly to get project ID.
    
    
    # 51. DB Connection Helper
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from src.config import settings
    from src.models import Project, VMUsage, VMInstance

    db_url = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    
    db = SessionLocal()
    project = db.query(Project).filter(Project.name == project_name).first()
    project_id = project.id
    log(f"Project ID: {project_id}")

    # 2. Create VM (Start Billing)
    vm_name = f"meter-vm-{int(time.time())}"
    log(f"Creating VM '{vm_name}' with Flavor ID 1 (Gaming Std)...")
    r = requests.post(f"{BASE_URL}/api/vm", json={
        "name": vm_name,
        "flavor_id": 1, # Gaming Std ($0.50)
        "project_id": project_id
    })
    log(f"Create VM Resp: {r.json()}")
    assert r.status_code == 200

    log("Sleeping 3 seconds (Simulating usage)...")
    time.sleep(3)

    # 3. Switch Model (Usage Segmentation)
    log("Switching to AI Model 2 (Llama-3-70B +$0.50)...")
    r = requests.post(f"{BASE_URL}/api/vm/{vm_name}/switch_model", json={
        "new_model_id": 2
    })
    log(f"Switch Model Resp: {r.json()}")
    assert r.status_code == 200

    log("Sleeping 3 seconds (Simulating usage)...")
    time.sleep(3)

    # 4. Delete VM (Stop Billing)
    log("Deleting VM...")
    r = requests.delete(f"{BASE_URL}/api/vm/{vm_name}")
    log(f"Delete Resp: {r.json()}")
    assert r.status_code == 200

    # 5. Audit DB
    db.expire_all()
    vm = db.query(VMInstance).filter(VMInstance.name == vm_name).first()
    usages = db.query(VMUsage).filter(VMUsage.vm_id == vm.id).all()
    
    log("--- BILLING AUDIT ---")
    total_bill = 0.0
    for u in usages:
        log(f"Session {u.id}: Duration={u.duration_seconds}s, HW=${u.applied_hw_rate}/hr, Model=${u.applied_model_rate}/hr, Cost=${u.total_cost}")
        total_bill += float(u.total_cost)
        
    log(f"Total Bill: ${round(total_bill, 6)}")
    
    if len(usages) == 2:
        print("✅ SUCCESS: Usage segmented into 2 records.")
    else:
        print(f"❌ FAIL: Expected 2 usage records, found {len(usages)}")

    db.close()

if __name__ == "__main__":
    run_test()
