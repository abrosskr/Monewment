from .base import BaseRecipeParser
from bs4 import BeautifulSoup
import json

class CookpadParser(BaseRecipeParser):
    site_name = "cookpad"
    country = "JP"
    language = "ja"

    def extract_links(self, soup: BeautifulSoup) -> list[str]:
        links = []
        for a in soup.find_all('a', href=True):
            if '/recipe/' in a['href']:
                links.append(f"https://cookpad.com{a['href']}" if a['href'].startswith('/') else a['href'])
        return list(set(links))

    def parse_recipe(self, soup: BeautifulSoup, url: str) -> dict:
        data = self.get_initial_schema(url, "Unknown")
        data["source_html_hash"] = self.calculate_hash(str(soup))

        # Cookpad uses structured scripts
        title_tag = soup.select_one('h1.recipe-title')
        if title_tag: data["title"] = title_tag.text.strip()

        # Ingredients (Japanese specific selectors)
        ing_tags = soup.select('div#ingredients div.ingredient_row')
        data["ingredients"] = [i.text.strip().replace('\n', ' ') for i in ing_tags if i.text.strip()]

        # Steps
        step_tags = soup.select('div#steps div.step_text')
        data["steps"] = [s.text.strip() for s in step_tags if s.text.strip()]

        return data
