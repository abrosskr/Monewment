
import requests
import json

BASE_URL = "http://localhost:8001/api/v1"

def test_billing():
    # 1. Charge $50 to Project 7 (assuming it exists from previous tests)
    print("💳 Charging Project 7 $50...")
    payload = {
        "project_id": 7,
        "amount": 50.00,
        "payment_token": "tok_visa"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/billing/charge", json=payload)
        print(f"Charge Response ({resp.status_code}): {resp.text}")
        
        if resp.status_code == 200:
            # 2. Check Balance
            print("💰 Checking Balance...")
            resp_bal = requests.get(f"{BASE_URL}/billing/balance/7")
            print(f"Balance: {resp_bal.text}")
    except Exception as e:
        print(f"Test Failed: {e}")

if __name__ == "__main__":
    test_billing()
