import requests
import sys

def test_api():
    try:
        url = "http://127.0.0.1:8000/api/admin/ants/status"
        print(f"Testing {url}...")
        res = requests.get(url)
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.text}")
        
        if res.status_code == 200:
            print("✅ Monitoring API is accessible.")
        else:
            print("❌ Monitoring API failed.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
