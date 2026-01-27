import requests
import json
import sys

def pull_model():
    model_name = "nomic-embed-text"
    url = "http://localhost:11434/api/pull"
    
    print(f"🚀 Triggering pull for '{model_name}' via API...")
    
    try:
        # Stream=True to see progress
        response = requests.post(url, json={"name": model_name, "stream": True}, stream=True)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                status = data.get("status")
                
                # Show progress bar if available
                total = data.get("total")
                completed = data.get("completed")
                
                if total and completed:
                    percent = (completed / total) * 100
                    sys.stdout.write(f"\rDownloading: {percent:.1f}% - {status}")
                    sys.stdout.flush()
                else:
                    print(f"Status: {status}")
                    
                if status == "success":
                    print(f"\n✅ Model '{model_name}' pulled successfully!")
                    return True
                    
    except Exception as e:
        print(f"\n❌ Failed to pull model: {e}")
        return False

if __name__ == "__main__":
    pull_model()
