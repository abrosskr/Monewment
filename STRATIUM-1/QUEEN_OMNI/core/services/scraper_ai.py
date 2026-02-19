import httpx
import json
import logging
from typing import Optional, Dict
from bs4 import BeautifulSoup
from pathlib import Path

# Mock settings for now (or we can create a config.py)
class Settings:
    OLLAMA_URL = "http://localhost:11434/api/generate"
    LLM_MODEL = "llama3"

settings = Settings()
logger = logging.getLogger("ScraperAI")

class ScraperAI:
    """
    [Scraper AI - OMNI-CRAWLER]
    LLM extraction without DB side-effects.
    """
    
    @classmethod
    async def parse_with_llm(cls, html_content: str, url: str) -> Optional[Dict]:
        try:
            # 1. Pre-process HTML
            soup = BeautifulSoup(html_content, 'lxml')
            for script in soup(["script", "style", "svg", "header", "footer", "nav"]):
                script.decompose()
            
            text_content = soup.get_text(separator=' ', strip=True)[:10000] 

            system_prompt = """You are a Data Decomposition Engine...""" # Truncated for brevity, keep user logic
            user_prompt = f"""Extract a recipe ONLY from this raw_blob..."""

            payload = {
                "model": settings.LLM_MODEL,
                "prompt": system_prompt + "\n\n" + user_prompt, 
                "stream": False,
                "format": "json"
            }
            
            logger.info(f"🧠 [Scraper AI] Invoking Llama3 for {url}...")
            async with httpx.AsyncClient(timeout=90.0) as client:
                resp = await client.post(settings.OLLAMA_URL, json=payload)
            
            if resp.status_code == 200:
                result = resp.json()
                raw_json = result.get('response', '{}')
                parsed = json.loads(raw_json)
                
                if parsed.get('status') == 'ok' and parsed.get('data'):
                    data = parsed['data']
                    data['url'] = url
                    data['ai_generated'] = True
                    data['ai_evidence'] = parsed.get('evidence')
                    return data
            return None
        except Exception as e:
            logger.error(f"❌ [Scraper AI Error] {e}")
            return None
