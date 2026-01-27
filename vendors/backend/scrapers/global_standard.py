import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Optional, Dict, List
import random
import time

from fake_useragent import UserAgent

class GlobalStandardScraper:
    """
    [Universal Recipe Extractor]
    1. Attempts JSON-LD (Schema.org) extraction first.
    2. Falls back to CSS selectors from site_config.json.
    """
    
    def __init__(self, site_key: str):
        self.site_key = site_key
        self.session = requests.Session()
        self.config = self._load_config()
        self.ua = UserAgent()

    def _load_config(self) -> Dict:
        path = "backend/app/scrapers/site_config.json"
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f).get(self.site_key, {})
        except:
            return {}

    def _get_headers(self, url: Optional[str] = None) -> Dict:
        ua = self.ua.random
        domain = ""
        if url:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc

        return {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9,ko;q=0.8,ja;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": f"https://www.google.com/search?q={self.site_key}+recipes",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0"
        }

    def scrape(self, url: str) -> Optional[Dict]:
        try:
            response = self.session.get(url, headers=self._get_headers(url), timeout=15)
            if response.status_code != 200:
                print(f"   ❌ [Error] Status {response.status_code} for {url}")
                return None
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 1. JSON-LD Extraction
            recipe_data = self._extract_json_ld(soup)
            if recipe_data and recipe_data.get('name') and recipe_data.get('ingredients'):
                recipe_data['url'] = url
                return recipe_data
            
            # 2. CSS Fallback (If JSON-LD fails or is incomplete)
            return self._extract_css(soup, url)
            
        except Exception as e:
            print(f"   ❌ [Scraper Error] {e}")
            return None

    def _extract_json_ld(self, soup: BeautifulSoup) -> Optional[Dict]:
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                
                # Handle nested @graph or list of objects
                items = data if isinstance(data, list) else data.get('@graph', [data])
                
                for item in items:
                    if item.get('@type') == 'Recipe' or 'Recipe' in str(item.get('@type', '')):
                        return {
                            "name": item.get('name'),
                            "ingredients": [i for i in item.get('recipeIngredient', [])],
                            "steps": self._parse_json_steps(item.get('recipeInstructions', [])),
                            "image": self._parse_json_image(item.get('image'))
                        }
            except:
                continue
        return None

    def _parse_json_steps(self, raw_steps) -> List[str]:
        steps = []
        if isinstance(raw_steps, list):
            for s in raw_steps:
                if isinstance(s, dict):
                    steps.append(s.get('text', ''))
                else:
                    steps.append(str(s))
        elif isinstance(raw_steps, str):
            steps = [raw_steps]
        return [s.strip() for s in steps if s.strip()]

    def _parse_json_image(self, raw_image) -> Optional[str]:
        if isinstance(raw_image, list) and raw_image:
            return raw_image[0]
        if isinstance(raw_image, dict):
            return raw_image.get('url')
        return str(raw_image) if raw_image else None

    def _extract_css(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        if not self.config:
            return None
            
        data = {"url": url, "name": None, "ingredients": [], "steps": [], "image": None}
        
        # Title
        title_elem = soup.select_one(self.config.get("title", ""))
        if title_elem:
            data['name'] = title_elem.text.strip()
            
        # Ingredients
        ing_elems = soup.select(self.config.get("ingredients", ""))
        data['ingredients'] = [re.sub(r'\s+', ' ', i.text).strip() for i in ing_elems if i.text.strip()]
        
        # Steps
        step_elems = soup.select(self.config.get("steps", ""))
        data['steps'] = [re.sub(r'\s+', ' ', s.text).strip() for s in step_elems if s.text.strip()]
        
        # Image
        img_elem = soup.select_one(self.config.get("image", ""))
        if img_elem:
            data['image'] = img_elem.get('src') or img_elem.get('data-src')
            
        return data if data['name'] and data['ingredients'] else None
