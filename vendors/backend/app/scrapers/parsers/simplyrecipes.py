from .base import BaseRecipeParser
from bs4 import BeautifulSoup
import json
import re

class SimplyrecipesParser(BaseRecipeParser):
    site_name = "simplyrecipes"
    country = "US"
    language = "en"

    def extract_links(self, soup: BeautifulSoup) -> list[str]:
        links = []
        # SimplyRecipes typically uses card list for search results
        for a in soup.find_all('a', href=True, class_='card'):
            links.append(a['href'])
        return list(set(links))

    def parse_recipe(self, soup: BeautifulSoup, url: str) -> dict:
        data = self.get_initial_schema(url, "Unknown")
        data["source_html_hash"] = self.calculate_hash(str(soup))

        # JSON-LD is very reliable on Dotdash Meredith sites
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                content = json.loads(script.string)
                items = content if isinstance(content, list) else content.get('@graph', [content])
                for item in items:
                    if item.get('@type') == 'Recipe':
                        data["title"] = item.get('name')
                        data["ingredients"] = item.get('recipeIngredient', [])
                        data["steps"] = [s.get('text') if isinstance(s, dict) else str(s) for s in item.get('recipeInstructions', [])]
                        data["cook_time_min"] = self._iso_to_min(item.get('cookTime'))
                        data["prep_time_min"] = self._iso_to_min(item.get('prepTime'))
                        data["total_time_min"] = self._iso_to_min(item.get('totalTime'))
                        data["servings"] = str(item.get('recipeYield', ''))
                        break
            except: continue
            
        return data

    def _iso_to_min(self, iso_str):
        if not iso_str: return None
        match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?', iso_str)
        if match:
            h = int(match.group(1) or 0)
            m = int(match.group(2) or 0)
            return h * 60 + m
        return None

if __name__ == "__main__":
    pass
