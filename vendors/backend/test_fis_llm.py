import requests
import json
from app.prompts import FIS_SYSTEM_PROMPT

def test_llm_fis_generation():
    print("🧠 [FIS LLM Test] Sending Recipe to Molecular Printer Engine...")
    
    # Test Input: Kimchi Jjigae
    user_input = "Kimchi Jjigae Recipe: 200g Aged Kimchi, 100g Pork Belly, 1T Soy Sauce, 0.5T Sugar, 1t Minced Garlic, 500ml Water."
    
    payload = {
        "model": "llama3", # Assuming 'llama3' or similar is installed in Ollama
        "messages": [
            {"role": "system", "content": FIS_SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ],
        "stream": False,
        "format": "json" # Enforce JSON output
    }
    
    try:
        response = requests.post("http://localhost:11434/api/chat", json=payload)
        response.raise_for_status()
        
        result = response.json()
        content = result["message"]["content"]
        
        print("\n🖨️  Molecular Printer Output (JSON):")
        parsed = json.loads(content)
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
        
        # Simple Validation
        instructions = parsed.get("inkjet_instructions", [])
        has_soy = any(i["name"] == "Soy_Sauce_Conc" for i in instructions)
        has_garlic = any(i["name"] == "Garlic_Onion_Conc" for i in instructions)
        
        if has_soy and has_garlic:
            print("\n✅ Success: LLM correctly mapped Soy Sauce and Garlic to Inks.")
        else:
            print("\n⚠️ Warning: Some key ingredients might be missing or mapped differently.")
            
    except Exception as e:
        print(f"\n❌ LLM Error: {e}")
        print("Ensure Ollama is running and 'llama3' model is pulled.")

if __name__ == "__main__":
    test_llm_fis_generation()
