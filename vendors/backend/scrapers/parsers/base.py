import hashlib
import datetime
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

class BaseRecipeParser(ABC):
    site_name: str
    country: str
    language: str

    @abstractmethod
    def extract_links(self, soup) -> List[str]:
        """Extract recipe links from search/index soup."""
        pass

    @abstractmethod
    def parse_recipe(self, soup, url: str) -> Optional[Dict[str, Any]]:
        """Parse recipe page into normalized schema."""
        pass

    def get_initial_schema(self, url: str, title: str) -> Dict[str, Any]:
        return {
            "site": self.site_name,
            "country": self.country,
            "language": self.language,
            "url": url,
            "title": title,
            "name": title,
            "ingredients": [],
            "steps": [],
            "cook_time_min": None,
            "prep_time_min": None,
            "total_time_min": None,
            "servings": None,
            "tags": [],
            "nutrition": {
                "calories": None,
                "protein_g": None,
                "fat_g": None,
                "carbs_g": None
            },
            "source_html_hash": None,
            "collected_at": datetime.datetime.now().isoformat()
        }

    def calculate_hash(self, html: str) -> str:
        return hashlib.sha256(html.encode("utf-8")).hexdigest()
