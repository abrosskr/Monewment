import requests
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Dict, Any

from app.engines.product_standard.models import ProductMaster
from app.engines.logistics.models import Supplier, ProductSourcing, ProductBatch
from app.engines.product_standard.codes import FulfillmentType, WeightUnit, ProductStatus

# ==========================================
# 1. EXTRACT LAYER (External Client)
# ==========================================
class ExternalDataClient:
    """
    Simulates fetching data from External Systems:
    1. FoodSafetyKorea (Processed Foods)
    2. Vendor ERP (Fresh Produce)
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def fetch_processed_foods(self) -> List[Dict]:
        """
        [Source: FoodSafetyKorea]
        Returns raw JSON list of processed food items.
        """
        print("📡 [ETL-Extract] Fetching Processed Foods from FoodSafetyKorea (Mock)...")
        # In real life, requests.get(f".../{self.api_key}/...")
        return [
            {
                "BRCD_NO": "8801043014856", 
                "PRDUCT_NM": "신라면", 
                "MANUFAC_NM": "(주)농심",
                "NUTR_CONT1": "500", "NUTR_CONT2": "79", "NUTR_CONT3": "10", "NUTR_CONT4": "16",
                "SERVING_SIZE": "120", 
                "BSSH_NM": "농심"
            },
            {
                "BRCD_NO": "8801048901045",
                "PRDUCT_NM": "햇반",
                "MANUFAC_NM": "씨제이제일제당(주)",
                "NUTR_CONT1": "310", "NUTR_CONT2": "68", "NUTR_CONT3": "5", "NUTR_CONT4": "2",
                "SERVING_SIZE": "210", 
                "BSSH_NM": "CJ제일제당"
            },
            {
                "BRCD_NO": "8801111111111", 
                "PRDUCT_NM": "서울우유 1L",
                "MANUFAC_NM": "서울우유협동조합",
                "NUTR_CONT1": "650", "NUTR_CONT2": "45", "NUTR_CONT3": "30", "NUTR_CONT4": "35",
                "SERVING_SIZE": "1000", 
                "BSSH_NM": "서울우유"
            }
        ]

    def fetch_vendor_fresh_data(self) -> List[Dict]:
        """
        [Source: Vendor ERP]
        Returns raw JSON list of fresh produce availability.
        """
        print("📡 [ETL-Extract] Fetching Fresh Produce from Vendor ERPs (Mock)...")
        return [
            {
                "vendor_code": "V-FARM-001",
                "sku": "FRESH-MELON-001",
                "name": "성주 꿀 참외",
                "origin": "경북 성주",
                "grade": "특(Special)",
                "price": 25000,
                "harvest_date": "2024-05-20",
                "vendor_name": "성주행복농장",
                "gln": "8800000000001"
            },
            {
                "vendor_code": "V-MEAT-002",
                "sku": "FRESH-BEEF-KR-001",
                "name": "횡성 한우 등심 1++",
                "origin": "강원 횡성",
                "grade": "1++(No.9)",
                "price": 120000,
                "harvest_date": "2024-05-22",
                "vendor_name": "횡성축협",
                "gln": "8800000000002"
            }
        ]

# ==========================================
# 2. TRANSFORM LAYER (Data Sanitizer)
# ==========================================
from app.engines.product_standard.parser import ProductDataParser

# ... (Previous imports)

# ==========================================
# 2. TRANSFORM LAYER (Data Sanitizer)
# ==========================================
class DataTransformer:
    """
    Normalizes 'Dirty' External Data into 'Clean' Internal Models.
    """
    @staticmethod
    def normalize_processed(raw: Dict) -> Dict:
        """
        FoodSafetyKorea -> ProductMaster (PIM)
        """
        try:
            kcal = float(raw.get("NUTR_CONT1", 0) or 0)
            carbs = float(raw.get("NUTR_CONT2", 0) or 0)
            protein = float(raw.get("NUTR_CONT3", 0) or 0)
            fat = float(raw.get("NUTR_CONT4", 0) or 0)
            weight = float(raw.get("SERVING_SIZE", 0) or 0)
        except ValueError:
            kcal, carbs, protein, fat, weight = 0, 0, 0, 0, 0

        # Normalize GTIN
        gtin = ProductDataParser.normalize_gtin(raw["BRCD_NO"])

        return {
            "gtin": gtin,
            "product_name": raw["PRDUCT_NM"],
            "brand": raw["BSSH_NM"],
            "manufacturer": raw["MANUFAC_NM"],
            "net_weight": weight,
            "weight_unit": WeightUnit.G, # Assumption
            "category_main": "PROCESSED",
            "nutrition_json": {
                "kcal": kcal, "carbs": carbs, "protein": protein, "fat": fat
            }
        }

    @staticmethod
    def normalize_fresh(raw: Dict) -> Dict:
        """
        Vendor ERP -> PIM + SCM
        """
        # Calculate raw GTIN logic first
        raw_gtin_suffix = raw["sku"][-6:]
        raw_gtin_string = raw["gln"][-7:] + raw_gtin_suffix
        
        # Normalize
        gtin = ProductDataParser.normalize_gtin(raw_gtin_string)

        return {
            # PIM Identity
            "gtin": gtin, 
            "sku": raw["sku"],
            "product_name": raw["name"],
            "sub_name": f"Grade: {raw['grade']}",
            "origin_country": "Korea", 
            "manufacturer": raw["vendor_name"], 
            "category_main": "FRESH",
            
            # SCM Data
            "vendor_name": raw["vendor_name"],
            "vendor_gln": raw["gln"],
            "cost_price": raw["price"],
            "origin_detail": raw["origin"],
            "harvest_date": raw["harvest_date"]
        }

# ==========================================
# 3. LOAD LAYER (Pipeline Runner)
# ==========================================
class EtlPipeline:
    def __init__(self, db: Session):
        self.db = db
        self.client = ExternalDataClient()
        self.transformer = DataTransformer()

    def run(self):
        print("\n🚀 [ETL-Load] Starting Data Ingestion Pipeline...")
        self._load_processed_foods()
        self._load_fresh_produce()
        print("✨ [ETL-Load] Pipeline Finished successfully.\n")

    def _load_processed_foods(self):
        raw_items = self.client.fetch_processed_foods()
        for raw in raw_items:
            data = self.transformer.normalize_processed(raw)
            # UPSERT PIM
            existing = self.db.query(ProductMaster).filter_by(gtin=data['gtin']).first()
            if not existing:
                product = ProductMaster(
                    gtin=data['gtin'],
                    product_name=data['product_name'],
                    brand=data['brand'],
                    manufacturer=data['manufacturer'],
                    net_weight=data['net_weight'],
                    weight_unit=data['weight_unit'],
                    category_main=data['category_main'],
                    nutrition_json=data['nutrition_json']
                )
                self.db.add(product)
                print(f"   ✅ [PIM-Insert] {data['product_name']} ({data['gtin']})")
                
                # NOTE: For processed foods, we assume a generic "Mart" supplier if none exists,
                # but currently we only seed the spec.
            else:
                print(f"   ℹ️ [PIM-Skip] {data['product_name']} already exists.")
        self.db.commit()

    def _load_fresh_produce(self):
        raw_items = self.client.fetch_vendor_fresh_data()
        for raw in raw_items:
            data = self.transformer.normalize_fresh(raw)
            
            # 1. Ensure Supplier (SCM)
            supplier = self.db.query(Supplier).filter_by(gln_code=data['vendor_gln']).first()
            if not supplier:
                supplier = Supplier(
                    name=data['vendor_name'],
                    gln_code=data['vendor_gln'],
                    contact_info={"type": "Direct Farm"}
                )
                self.db.add(supplier)
                self.db.flush() # Get ID
                print(f"   🏢 [SCM-Supplier] Registered {data['vendor_name']}")

            # 2. Ensure Product Master (PIM)
            # Fresh produce GTINs are tricky, we use a generated one or SKU mapping
            gtin = data['gtin'] if len(data['gtin']) <= 14 else data['gtin'][:14] 
            
            product = self.db.query(ProductMaster).filter_by(gtin=gtin).first()
            if not product:
                product = ProductMaster(
                    gtin=gtin,
                    sku=data['sku'],
                    product_name=data['product_name'],
                    sub_name=data['sub_name'],
                    manufacturer=data['manufacturer'],
                    brand="Nature's Best", # Generic Brand for fresh
                    origin_country=data['origin_country'],
                    category_main=data['category_main'],
                    net_weight=1.0, # Placeholder
                    weight_unit=WeightUnit.KG
                )
                self.db.add(product)
                self.db.flush()
                print(f"   🥦 [PIM-Insert] {data['product_name']}")
            
            # 3. Create Deal (SCM)
            # Check if deal exists
            deal = self.db.query(ProductSourcing).filter(
                ProductSourcing.product_gtin == product.gtin,
                ProductSourcing.supplier_id == supplier.supplier_id
            ).first()
            
            if not deal:
                deal = ProductSourcing(
                    product_gtin=product.gtin,
                    supplier_id=supplier.supplier_id,
                    fulfillment_type=FulfillmentType.DROP_SHIPPING,
                    cost_price_vat_exclusive=data['cost_price'],
                    moq=1,
                    lead_time_days=2
                )
                self.db.add(deal)
                self.db.flush()
                print(f"   🚚 [SCM-Deal] Signed DropShipping contract for {data['product_name']}")

            # 4. Receive Batch (Traceability)
            # Every ETL run simulates a new daily harvest being available
            # We prevent duplicate batch for same day/lot
            harvest_date_obj = date.fromisoformat(data['harvest_date'])
            batch = self.db.query(ProductBatch).filter(
                ProductBatch.sourcing_id == deal.sourcing_id,
                ProductBatch.lot_number == f"HARVEST-{data['harvest_date']}"
            ).first()
            
            if not batch:
                batch = ProductBatch(
                    sourcing_id=deal.sourcing_id,
                    lot_number=f"HARVEST-{data['harvest_date']}",
                    harvest_date=harvest_date_obj,
                    initial_quantity=100,
                    current_quantity=100,
                    status=ProductStatus.ACTIVE
                )
                self.db.add(batch)
                print(f"   📦 [SCM-Batch] Ingested {data['product_name']} Lot: {batch.lot_number}")
                
        self.db.commit()
