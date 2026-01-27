from .allrecipes import AllrecipesParser
from .simplyrecipes import SimplyrecipesParser
from .bbc_goodfood import BbcgoodfoodParser
from .cookpad import CookpadParser
from .marmiton import MarmitonParser
from .recipe10k import Recipe10kParser

PARSER_REGISTRY = {
    "allrecipes": AllrecipesParser,
    "simplyrecipes": SimplyrecipesParser,
    "bbcgoodfood": BbcgoodfoodParser,
    "bbc_goodfood": BbcgoodfoodParser,
    "cookpad": CookpadParser,
    "cookpad_jp": CookpadParser,
    "marmiton": MarmitonParser,
    "recipe10k": Recipe10kParser,
    "10000recipe": Recipe10kParser,
}

def get_parser(site_key: str):
    return PARSER_REGISTRY.get(site_key)
