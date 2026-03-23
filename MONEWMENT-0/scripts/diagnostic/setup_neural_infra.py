import httpx
import asyncio
import logging
import sys

# --- [LOGGING CONFIG] ---
logging.basicConfig(level=logging.INFO, format="[NEURAL-INFRA] %(levelname)s: %(message)s")
logger = logging.getLogger("neural_setup")

OLLAMA_API = "http://127.0.0.1:11434/api"

MODELS = {
    "monewment-areum": {
        "from": "gemma2:2b",
        "system": (
            "You are monewment-areum, a Senior Sensory Unit for the MONEWMENT Empire. "
            "Persona: 'The Butcher'. You are surgically precise. "
            "Goal: Extract clinical, objective facts from raw data. "
            "Output: Respond ONLY with valid JSON matching the 'Essence' schema. "
            "No small talk. No explanation. Just JSON."
        )
    },
    "monewment-rex": {
        "from": "llama3.1:8b",
        "system": (
            "You are monewment-rex, the Imperial Strategist for the MONEWMENT Empire. "
            "Persona: 'The Ruler'. You oversee all domains. "
            "Goal: Synthesize domain reports into a powerful Global Strategy. "
            "Output: Respond ONLY with valid JSON matching the 'GlobalStrategy' schema."
        )
    }
}

async def create_persona(client: httpx.AsyncClient, name: str, config: dict):
    logger.info(f"Injecting persona: {name} (base: {config['from']})...")
    try:
        r = await client.post(f"{OLLAMA_API}/create", json={
            "name": name,
            "modelfile": f"FROM {config['from']}\nSYSTEM \"{config['system']}\""
        }, timeout=300.0)
        
        # Ollama /create can be a stream or a single response depending on version
        if r.status_code == 200:
            logger.info(f"✅ Persona {name} injected successfully.")
        else:
            logger.error(f"❌ Failed to inject {name}: {r.text}")
    except Exception as e:
        logger.error(f"Error creating {name}: {e}")

async def main():
    async with httpx.AsyncClient() as client:
        # Check connection
        try:
            await client.get(f"{OLLAMA_API}/tags", timeout=5.0)
        except Exception:
            logger.error("Ollama is not running. Please start Ollama before setup.")
            sys.exit(1)
            
        tasks = [create_persona(client, name, config) for name, config in MODELS.items()]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
