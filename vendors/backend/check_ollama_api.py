import requests
import sys

def check_ollama():
    try:
        # Check if service is up
        print("🔍 Checking Ollama Service at http://localhost:11434...")
        health = requests.get("http://localhost:11434/")
        if health.status_code == 200:
            print("✅ Ollama Service is RUNNING.")
        else:
            print(f"⚠️ Ollama Service responded with {health.status_code}")
            
        # Check available models
        print("\n🔍 Checking Models...")
        tags = requests.get("http://localhost:11434/api/tags")
        if tags.status_code == 200:
            models = tags.json().get('models', [])
            if models:
                print(f"✅ Found {len(models)} models:")
                for m in models:
                    print(f"  - {m['name']}")
                
                # Check for llama3
                has_llama3 = any('llama3' in m['name'] for m in models)
                if has_llama3:
                    print("\n🎉 Llama3 is ready!")
                else:
                    print("\n⚠️ Llama3 is NOT found. You need to run 'ollama pull llama3'")
            else:
                print("⚠️ No models found. Please run 'ollama pull llama3'")
        
    except Exception as e:
        print(f"❌ Could not connect to Ollama: {e}")
        print("Please ensure Ollama is installed and running in the system tray.")

if __name__ == "__main__":
    check_ollama()
