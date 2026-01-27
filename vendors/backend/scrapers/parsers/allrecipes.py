from .base import BaseRecipeParser
from bs4 import BeautifulSoup
import json
import re

class AllrecipesParser(BaseRecipeParser):
    site_name = "allrecipes"
    country = "US"
    language = "en"

    def extract_links(self, soup: BeautifulSoup) -> list[str]:
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Match standard recipe patterns
            if '/recipe/' in href and not any(x in href for x in ['/search', '/user', '/gallery']):
                 links.append(href)
        return list(set(links))

    def parse_recipe(self, soup: BeautifulSoup, url: str) -> dict:
        data = self.get_initial_schema(url, "Unknown")
        data["source_html_hash"] = self.calculate_hash(str(soup))

        # 1. Try JSON-LD
        json_ld = self._extract_json_ld(soup)
        if json_ld:
            data.update(json_ld)
        
        # 2. BS4 Fallback/Refinement
        if data["title"] == "Unknown":
            title_tag = soup.select_one('h1.heading-content') or soup.find('h1')
            if title_tag: data["title"] = title_tag.text.strip()

        if not data["ingredients"]:
            ing_tags = soup.select('ul.ingredients-section li')
            data["ingredients"] = [i.text.strip() for i in ing_tags if i.text.strip()]

        if not data["steps"]:
            step_tags = soup.select('fieldset.instructions-section__fieldset li p')
            data["steps"] = [s.text.strip() for s in step_tags if s.text.strip()]

        return data

    def _extract_json_ld(self, soup):
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                content = json.loads(script.string)
                items = content if isinstance(content, list) else [content]
                for item in items:
                    if item.get('@type') == 'Recipe':
                        return {
                            "title": item.get('name'),
                            "ingredients": item.get('recipeIngredient', []),
                            "steps": self._parse_json_steps(item.get('recipeInstructions', [])),
                            "total_time_min": self._iso_to_min(item.get('totalTime')),
                            "servings": str(item.get('recipeYield', [None])[0]) if isinstance(item.get('recipeYield'), list) else str(item.get('recipeYield'))
                        }
            except: continue
        return None

    def _parse_json_steps(self, raw):
        steps = []
        for r in raw:
            if isinstance(r, dict): steps.append(r.get('text', ''))
            else: steps.append(str(r))
        return [s.strip() for s in steps if s.strip()]

    def _iso_to_min(self, iso_str):
        if not iso_str: return None
        # Simple extraction e.g. PT1H30M
        match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?', iso_str)
        if match:
            h = int(match.group(1) or 0)
            m = int(match.group(2) or 0)
            return h * 60 + m
        return None

if __name__ == "__main__":
    # Test stub
    pass
