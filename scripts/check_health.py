
import requests

def test_health():
    try:
        r = requests.get("http://localhost:8001/")
        print(f"Health Check: {r.status_code}")
        
        # Check Project Structure (Tests relative path resolution in collector.py)
        # We assume project 'test' exists or just check if it returns 404/200 but doesn't crash.
        r = requests.get("http://localhost:8001/api/projects/sample_vmi/structure")
        print(f"Structure Check: {r.status_code}")
        if r.status_code == 200:
            print("Structure API: Success")
            
    except Exception as e:
        print(f"Verification Failed: {e}")

if __name__ == "__main__":
    test_health()
