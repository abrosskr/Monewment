from .base import BaseRecipeParser
from bs4 import BeautifulSoup
import json
import re

class BbcgoodfoodParser(BaseRecipeParser):
    site_name = "bbc_goodfood"
    country = "UK"
    language = "en"

    def extract_links(self, soup: BeautifulSoup) -> list[str]:
        links = []
        base = "https://www.bbcgoodfood.com"
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/recipes/' in href and not any(x in href for x in ['/search', '/category', '/collection']):
                full_url = f"{base}{href}" if href.startswith('/') else href
                links.append(full_url)
        return list(set(links))

    def parse_recipe(self, soup: BeautifulSoup, url: str) -> dict:
        data = self.get_initial_schema(url, "Unknown")
        data["source_html_hash"] = self.calculate_hash(str(soup))

        # BBC Good Food uses structured JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                content = json.loads(script.string)
                if isinstance(content, list):
                    recipe_item = next((i for i in content if i.get('@type') == 'Recipe'), None)
                else:
                    recipe_item = content if content.get('@type') == 'Recipe' else None
                
                if recipe_item:
                    data["title"] = recipe_item.get('name')
                    data["ingredients"] = recipe_item.get('recipeIngredient', [])
                    data["steps"] = [s.get('text') if isinstance(s, dict) else str(s) for s in recipe_item.get('recipeInstructions', [])]
                    data["total_time_min"] = self._iso_to_min(recipe_item.get('totalTime'))
                    break
            except: continue
        
        # Fallback for ingredients (BBC layout changes)
        if not data["ingredients"]:
            ing_tags = soup.select('ul.recipe__ingredients-list li')
            data["ingredients"] = [i.text.strip() for i in ing_tags if i.text.strip()]

        return data

    def _iso_to_min(self, iso_str):
        if not iso_str: return None
        match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?', iso_str)
        if match:
            h = int(match.group(1) or 0)
            m = int(match.group(2) or 0)
            return h * 60 + m
        return None
