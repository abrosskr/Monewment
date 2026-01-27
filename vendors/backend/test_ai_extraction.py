import requests
import json

def test_extraction():
    url = "http://localhost:8011/v1/analyze/text"
    payload = {
        "text": "Make a pasta with tomato, parmesan and basil."
    }
    
    print(f"🧪 Testing AI Extraction with text: '{payload['text']}'")
    try:
        response = requests.post(url, json=payload, timeout=40)
        if response.status_code == 200:
            print("✅ Success!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_extraction()
