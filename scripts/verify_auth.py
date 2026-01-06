
import requests
import time

BASE_URL = "http://localhost:8001"

def test_jwt_auth():
    # 1. Signup
    email = f"jwt_test_{int(time.time())}@test.com"
    password = "secure_password123"
    r = requests.post(f"{BASE_URL}/api/auth/signup", json={
        "email": email, "password": password, "name": "JwtTester"
    })
    print(f"Signup: {r.status_code}")
    assert r.status_code == 200

    # 2. Login (JWT Generation)
    r = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": email, "password": password
    })
    print(f"Login: {r.status_code}")
    assert r.status_code == 200
    token = r.json().get("access_token")
    print(f"Token acquired: {token[:20]}...")

    # 3. Protected Route (Success with Header)
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    print(f"Protected Profile: {r.status_code}")
    assert r.status_code == 200
    print(f"Profile Data: {r.json()}")
    assert r.json().get("email") == email

    # 4. Protected Route (Fail - Missing Token)
    r = requests.get(f"{BASE_URL}/api/auth/me")
    print(f"Protected (No Token): {r.status_code}")
    assert r.status_code == 401

    # 5. Protected Route (Fail - Invalid Token)
    headers = {"Authorization": "Bearer invalid_token"}
    r = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    print(f"Protected (Invalid Token): {r.status_code}")
    assert r.status_code == 401

    print("✅ JWT Authentication flow verified!")

if __name__ == "__main__":
    test_jwt_auth()
