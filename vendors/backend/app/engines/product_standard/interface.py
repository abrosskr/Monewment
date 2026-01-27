from sqlalchemy.orm import Session
from typing import Optional, List
from .models import ProductMaster
from .parser import ProductDataParser

class ProductStandardInterface:
    """
    [Public API]
    Allows other services (Nutrition, Search, Scanner) to access Master Data.
    """
    
    def __init__(self, db: Session):
        self.db = db

    def get_by_gtin(self, raw_code: str) -> Optional[ProductMaster]:
        """
        [Barcode Scanner Entry]
        Normalization -> Lookup.
        """
        clean_gtin = ProductDataParser.normalize_gtin(raw_code)
        # Try exact 14-digit match
        # (In real logic, might need to check if DB stores 13 or 14 digits. 
        #  Our Parser pads to 14, so we assume DB stores 14.)
        return self.db.query(ProductMaster).filter(ProductMaster.gtin == clean_gtin).first()

    def search_by_name(self, query: str) -> List[ProductMaster]:
        """
        [Keyword Search]
        Used by NutritionService to find "Spaghetti".
        """
        # Simple LIKE search for prototype
        return self.db.query(ProductMaster).filter(
            ProductMaster.product_name.ilike(f"%{query}%")
        ).limit(5).all()

    def create_product(self, data: dict) -> ProductMaster:
        """
        Protected method for Admin/Seeding.
        """
        # Auto-normalize
        if "gtin" in data:
            data["gtin"] = ProductDataParser.normalize_gtin(data["gtin"])
            
        product = ProductMaster(**data)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product
