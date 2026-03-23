import sys
import os
import json
import time
import random
import hashlib
import logging
import httpx
from datetime import datetime
from bs4 import BeautifulSoup
from pathlib import Path

# --- [PATH RESOLUTION] ---
root = Path(__file__).resolve().parent.parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from core.robustness import get_imperial_client, wait_for_core

# Configure logging
logging.basicConfig(level=logging.INFO, format="[ANT-%(process)d] %(levelname)s: %(message)s")
logger = logging.getLogger("omni_crawler_ant")

CORE_API_URL = "http://127.0.0.1:8800/v1"
QUEEN_TOKEN = os.environ.get("QUEEN_TOKEN", "mon_gw_ch4ng3m3_bef0re_pr0d")

# [Phase A: 부화 및 자아 인식]
vow = {}
try:
    with open("identity.vow", "r") as f:
        vow = json.load(f)
    INSTANCE_ID = vow.get("instance_id", "UNKNOWN_ANT")
    STRATUM_ID = vow.get("parent_stratum", "UNKNOWN_STRATUM")
    logger.info(f"Identity recognized. I am {INSTANCE_ID}, serving {STRATUM_ID}.")
except FileNotFoundError:
    logger.warning("No identity.vow found. Operating as an anonymous rogue ant.")
    INSTANCE_ID = "ROGUE_ANT"
    STRATUM_ID = "DEV_STRATUM"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0"
]

def save_to_local_pillar(url: str, raw_html: str, essence: str, content_hash: str) -> str:
    """[IMPERIAL] Save high-density assets to local hardware storage."""
    today = datetime.now().strftime("%Y-%m-%d")
    storage_dir = Path("data/raw") / STRATUM_ID / today
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = storage_dir / f"{content_hash}.json"
    payload = {
        "url": url,
        "raw_html": raw_html,
        "essence": essence,
        "metadata": {
            "ant_id": INSTANCE_ID,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    
    logger.info(f"[PILLAR] Asset stored locally: {file_path}")
    return str(file_path.absolute())

def fetch_url(url: str, retries=3) -> httpx.Response:
    delay = 3.0
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    for attempt in range(1, retries + 1):
        try:
            with httpx.Client(timeout=15.0, follow_redirects=True) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()
                return response
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            if attempt == retries:
                logger.error(f"Fetch failed definitively after {retries} attempts: {e}")
                raise
            logger.warning(f"Fetch attempt {attempt} failed: {e}. Retrying in {delay}s...")
            time.sleep(delay)
            delay *= 2.0

def parse_html(html_content: str, url: str) -> dict:
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract Title
    title = ""
    if soup.title:
        title = soup.title.string.strip()
    elif soup.find('h1'):
        title = soup.find('h1').text.strip()
    
    # [V51.5] Essence Extraction: DOM Structure only
    for noise in soup(["script", "style", "nav", "footer", "header"]):
        noise.decompose()
    
    essence = str(soup)
    cleaned_text = " ".join(soup.stripped_strings)
    
    return {
        "title": title,
        "text": cleaned_text,
        "essence": essence
    }

def calculate_hash(title: str, text: str) -> str:
    payload = f"{title}|{len(text)}|{hashlib.md5(text.encode()).hexdigest()}"
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()

def report_coordinate_to_core(payload: dict):
    """[HYBRID] Report ONLY coordinates and hash to the core API."""
    headers = {
        "X-Queen-Token": QUEEN_TOKEN,
        "X-Alias": "ANT",
        "X-Stratum-ID": STRATUM_ID,
        "Content-Type": "application/json"
    }
    
    with get_imperial_client(is_async=False, timeout=10.0) as client:
        # Endpoint expects coordinate format now
        resp = client.post(f"{CORE_API_URL}/pipeline/coordinate", headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()

def run_task(target_url: str):
    logger.info(f"Target Acquired: {target_url}")
    
    try:
        response = fetch_url(target_url)
        raw_html = response.text
    except Exception as e:
        logger.error(f"Extraction aborted for {target_url}")
        return False
        
    try:
        parsed_data = parse_html(raw_html, target_url)
        cleaned_text = parsed_data["text"]
        essence = parsed_data["essence"]
        title = parsed_data["title"]
    except Exception as e:
        logger.error(f"Parsing failed for {target_url}: {e}")
        return False
        
    content_hash = calculate_hash(title, cleaned_text)
    
    # 3. [NEW] Save to Local Pillar
    file_path = save_to_local_pillar(target_url, raw_html, essence, content_hash)
    
    # 4. [HYBRID] Payload with Coordinate only
    payload = {
        "url": target_url,
        "file_path": file_path,
        "content_hash": content_hash,
        "accumulated_cost": 0.0, # Placeholder for real cost calc
        "vendor_id": None
    }
    
    # 5. Report Coordinate (MUST bypass proxy)
    try:
        report_coordinate_to_core(payload)
        logger.info(f"Successfully reported coordinate: {content_hash}")
        # Phase E: Explicit Memory Clear
        del raw_html
        del cleaned_text
        del essence
        del payload
    except Exception as e:
        logger.error(f"Reporting coordinate failed for {target_url}: {e}")
        return False
        
    return True

if __name__ == "__main__":
    logger.info("HYBRID OMNI-CRAWLER ANT Booting...")
    
    if len(sys.argv) > 1:
        run_task(sys.argv[1])
    else:
        logger.warning("No target URL provided.")
    
    delay = random.uniform(2.0, 5.0)
    logger.info(f"Mission concluded. Sleeping for {delay:.2f}s.")
    time.sleep(delay)
    sys.exit(0)
