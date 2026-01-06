
import requests

BASE_URL = "http://localhost:8001"

def test_admin_apis():
    print("--- 🛠️ Admin Dashboard API Verification ---")
    
    # 1. Stats
    r = requests.get(f"{BASE_URL}/api/admin/stats")
    print(f"Admin Stats: {r.status_code}")
    assert r.status_code == 200
    print(f"Stats Data: {r.json()}")

    # 2. VM List
    r = requests.get(f"{BASE_URL}/api/admin/vms")
    print(f"All VMs: {r.status_code}")
    assert r.status_code == 200
    print(f"VM Count: {len(r.json().get('vms', []))}")

    # 3. Pricing List
    r = requests.get(f"{BASE_URL}/api/admin/pricing/flavors")
    print(f"Pricing Flavors: {r.status_code}")
    assert r.status_code == 200
    flavors = r.json().get('flavors', [])
    print(f"Flavors found: {[f['name'] for f in flavors]}")

    # 4. Pricing Update (Test on first flavor)
    if flavors:
        fid = flavors[0]['id']
        old_rate = flavors[0]['hourly_rate']
        new_rate = old_rate + 100.0
        
        r = requests.patch(f"{BASE_URL}/api/admin/pricing/flavors/{fid}", json={
            "hourly_rate": new_rate
        })
        print(f"Update Price (Flavor {fid}): {r.status_code}")
        assert r.status_code == 200
        assert r.json()['new_rate'] == new_rate
        
        # Revert
        requests.patch(f"{BASE_URL}/api/admin/pricing/flavors/{fid}", json={
            "hourly_rate": old_rate
        })
        print("Reverted price back to original.")

    print("\n✅ Admin Dashboard APIs verified!")

if __name__ == "__main__":
    test_admin_apis()
