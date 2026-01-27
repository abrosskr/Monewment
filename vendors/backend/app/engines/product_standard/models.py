from sqlalchemy import Column, String, Integer, Float, Enum, JSON, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base
from app.engines.product_standard.codes import WeightUnit

# ============================================================
# Product Master (Abstract Specification)
# ============================================================
class ProductMaster(Base):
    """
    [PIM Engine]
    Standard Product Definitions. Immutable Facts only.
    No Price, No Supplier, No Stock here.
    """
    __tablename__ = "product_master_std"

    # Identity
    gtin = Column(String(14), primary_key=True, index=True, comment="GTIN-13/14 Barcode (Global Key)")
    sku = Column(String(50), nullable=True, index=True, comment="Internal SKU for legacy support")
    
    # Classification
    manufacturer = Column(String(100), nullable=False, index=True, comment="Brand Owner (e.g. Ottogi)")
    brand = Column(String(100), nullable=False, index=True)
    origin_country = Column(String(50), default="Korea")
    category_main = Column(String(50), index=True)
    category_sub = Column(String(50), index=True)
    kan_code = Column(String(20), nullable=True, comment="Korean KAN Code")

    # Display
    product_name = Column(String(200), nullable=False, index=True)
    sub_name = Column(String(200), nullable=True)
    
    # Specs (Physics)
    net_weight = Column(Float, nullable=False, comment="Weight Value (e.g. 500)")
    weight_unit = Column(Enum(WeightUnit), default=WeightUnit.G)

    # Specs (Market) - RECOMMENDATIONS ONLY
    msrp = Column(Integer, nullable=True, comment="Recommended Retail Price (Reference)")
    shelf_life_desc = Column(String(100), nullable=True, comment="General Expiration Rule (e.g. 1 year)")

    # Intelligence & Integration
    nutrition_json = Column(JSON, nullable=True, comment="Per 100g/ml or Per Serving specs")
    chemical_json = Column(JSON, nullable=True, comment="FIS Chemical Composition")
    is_ink = Column(Boolean, default=False, index=True, comment="Is this a FIS Printer Ink?")
    
    description_multilang = Column(JSON, nullable=True, comment="Global descriptions")
    image_url = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # NOTE: Relationships to Sourcing/Inventory are now handled in the Logistics Engine via FK.
