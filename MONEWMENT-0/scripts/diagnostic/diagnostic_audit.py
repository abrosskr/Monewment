
import psycopg, os, httpx, asyncio
from dotenv import load_dotenv
load_dotenv('MONEWMENT-0/.env')

async def diagnose():
    u, p, h, d = os.getenv('SUPABASE_USER'), os.getenv('SUPABASE_PASSWORD'), os.getenv('SUPABASE_HOST'), os.getenv('SUPABASE_DB')
    url = f'postgresql://{u}:{p}@{h}:6543/{d}'
    
    print("--- [DIAGNOSTIC] DB STATE ---")
    try:
        with psycopg.connect(url) as conn:
            cur = conn.cursor()
            cur.execute("SELECT pipeline_state, COUNT(*) FROM \"schema_stratum_stratum_4a14e6ca\".assets GROUP BY pipeline_state")
            print(f"States: {cur.fetchall()}")
    except Exception as e:
        print(f"DB Error: {e}")

    print("\n--- [DIAGNOSTIC] OLLAMA ---")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://127.0.0.1:11434/api/tags", timeout=5)
            print(f"Ollama Status: {resp.status_code}")
            print(f"Models: {[m['name'] for m in resp.json().get('models', [])]}")
    except Exception as e:
        print(f"Ollama Error: {e}")

if __name__ == "__main__":
    asyncio.run(diagnose())
