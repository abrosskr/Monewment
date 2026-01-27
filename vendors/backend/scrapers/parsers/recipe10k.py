from .base import BaseRecipeParser
from bs4 import BeautifulSoup
import json
import re

class Recipe10kParser(BaseRecipeParser):
    site_name = "10000recipe"
    country = "KR"
    language = "ko"

    def extract_links(self, soup: BeautifulSoup) -> list[str]:
        links = []
        base = "https://www.10000recipe.com"
        for a in soup.find_all('a', href=True):
            if '/recipe/' in a['href'] and '/recipe/list.html' not in a['href']:
                links.append(f"{base}{a['href']}" if a['href'].startswith('/') else a['href'])
        return list(set(links))

    def parse_recipe(self, soup: BeautifulSoup, url: str) -> dict:
        data = self.get_initial_schema(url, "Unknown")
        data["source_html_hash"] = self.calculate_hash(str(soup))

        title_tag = soup.select_one('div.view2_summary h3')
        if title_tag:
            data["title"] = title_tag.text.strip()
            data["name"] = data["title"] # Ensure compatibility

        # Ingredients (KR specific)
        ing_area = soup.select_one('div.ready_ingre3')
        if ing_area:
            ing_tags = ing_area.select('li')
            data["ingredients"] = [i.text.strip().replace('\n', '').replace('  ', ' ') for i in ing_tags if i.text.strip()]

        # Steps
        step_tags = soup.select('div.view_step div.view_step_cont')
        data["steps"] = [s.text.strip() for s in step_tags if s.text.strip()]

        return data
