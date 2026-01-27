from .base import BaseRecipeParser
from bs4 import BeautifulSoup
import json
import re

class MarmitonParser(BaseRecipeParser):
    site_name = "marmiton"
    country = "FR"
    language = "fr"

    def extract_links(self, soup: BeautifulSoup) -> list[str]:
        links = []
        base = "https://www.marmiton.org"
        for a in soup.find_all('a', href=True):
            if '/recettes/recette_' in a['href']:
                links.append(f"{base}{a['href']}" if a['href'].startswith('/') else a['href'])
        return list(set(links))

    def parse_recipe(self, soup: BeautifulSoup, url: str) -> dict:
        data = self.get_initial_schema(url, "Unknown")
        data["source_html_hash"] = self.calculate_hash(str(soup))

        # JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                content = json.loads(script.string)
                if content.get('@type') == 'Recipe':
                    data["title"] = content.get('name')
                    data["ingredients"] = content.get('recipeIngredient', [])
                    data["steps"] = [s.get('text') if isinstance(s, dict) else str(s) for s in content.get('recipeInstructions', [])]
                    break
            except: continue

        # BS4 Fallback
        if not data["ingredients"]:
            ing_tags = soup.select('span.ingredient-name')
            data["ingredients"] = [i.text.strip() for i in ing_tags if i.text.strip()]

        return data
