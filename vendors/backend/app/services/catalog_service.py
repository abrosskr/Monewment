from sqlalchemy.orm import Session
from app.engines.product_standard.models import ProductMaster
from app.engines.logistics.models import Supplier, ProductSourcing, ProductBatch
from app.engines.product_standard.interface import ProductStandardInterface
from app.engines.product_standard.codes import FulfillmentType, WeightUnit

class CatalogService:
    """
    [Service Layer]
    Orchestrates PIM (Product) and SCM (Logistics) initialization.
    Replaces old 'seed_products.py' scripts.
    """
    def __init__(self, db: Session):
        self.db = db
        self.pim_api = ProductStandardInterface(db)

    def initialize_catalog(self):
        """
        Seeds default Manufacturers, Products, and Logistics Deals.
        Idempotent: Checks existence before creating.
        """
        print("🌱 [CatalogService] Initializing Catalog Data...")
        self._seed_suppliers()
        self._seed_products_and_deals()
        print("✅ [CatalogService] Initialization Complete.")

    def _seed_suppliers(self):
        suppliers = [
            {"name": "Ottogi Logistics", "gln": "8801045000000", "manager": "Kim"},
            {"name": "CJ CheilJedang", "gln": "8801005000000", "manager": "Lee"},
            {"name": "Divella Italy", "gln": "8005121000000", "manager": "Mario"},
        ]
        
        for s in suppliers:
            exists = self.db.query(Supplier).filter(Supplier.name == s["name"]).first()
            if not exists:
                sup = Supplier(
                    name=s["name"], 
                    gln_code=s["gln"], 
                    contact_info={"manager": s["manager"]}
                )
                self.db.add(sup)
        self.db.commit()

    def _seed_products_and_deals(self):
        # Retrieve Suppliers (Assume they exist now)
        sup_ottogi = self.db.query(Supplier).filter(Supplier.name == "Ottogi Logistics").first()
        sup_cj = self.db.query(Supplier).filter(Supplier.name == "CJ CheilJedang").first()
        sup_divella = self.db.query(Supplier).filter(Supplier.name == "Divella Italy").first()
        
        items = [
            {
                "gtin": "8801045000015", "brand": "오뚜기", "name": "옛날국수 소면",
                "weight": 900.0, "unit": WeightUnit.G, "cost": 2800, 
                "sup": sup_ottogi, "type": FulfillmentType.OWNED_INVENTORY,
                "nutrition": {"kcal": 340}
            },
            {
                "gtin": "8801005123456", "brand": "백설", "name": "하얀 설탕",
                "weight": 1000.0, "unit": WeightUnit.G, "cost": 1500,
                "sup": sup_cj, "type": FulfillmentType.OWNED_INVENTORY,
                "nutrition": {"kcal": 400}
            },
            {
                "gtin": "8005121210052", "brand": "Divella", "name": "Spaghetti Ristorante 8",
                "weight": 500.0, "unit": WeightUnit.G, "cost": 1100,
                "sup": sup_divella, "type": FulfillmentType.DROP_SHIPPING,
                "nutrition": {"kcal": 355}
            }
        ]
        
        for item in items:
            # 1. PIM: Create Spec
            if not self.pim_api.get_by_gtin(item["gtin"]):
                self.pim_api.create_product({
                    "gtin": item["gtin"],
                    "manufacturer": f"(주){item['brand']}", # Simplified
                    "brand": item["brand"],
                    "product_name": item["name"],
                    "net_weight": item["weight"],
                    "weight_unit": item["unit"],
                    "nutrition_json": item["nutrition"]
                })
            
            # 2. SCM: Create Deal
            # Check if deal exists
            exists = self.db.query(ProductSourcing).filter(
                ProductSourcing.product_gtin == item["gtin"],
                ProductSourcing.supplier_id == item["sup"].supplier_id
            ).first()
            
            if not exists:
                deal = ProductSourcing(
                    product_gtin=item["gtin"],
                    supplier_id=item["sup"].supplier_id,
                    fulfillment_type=item["type"],
                    cost_price_vat_exclusive=item["cost"],
                    moq=10
                )
                self.db.add(deal)
                
        self.db.commit()
