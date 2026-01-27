from sqlalchemy import Column, String, Integer, Float, Enum, JSON, DateTime, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.engines.product_standard.codes import FulfillmentType, ProductStatus

# ============================================================
# 1. Supplier Standard (Actor)
# ============================================================
class Supplier(Base):
    __tablename__ = "supplier_std"
    
    supplier_id = Column(Integer, primary_key=True, index=True)
    gln_code = Column(String(13), unique=True, index=True, nullable=True, comment="Global Location Number (13 digits)")
    name = Column(String(100), nullable=False, comment="Farm/Company Name (e.g. Seongju Farm 01)")
    biz_reg_number = Column(String(20), nullable=True, comment="Business Registration Number")
    
    contact_info = Column(JSON, nullable=True, comment="Manager name, Phone, Email")
    shipping_policy = Column(JSON, nullable=True, comment="Shipping rules (e.g. Free > 50k)")
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    sourcing_deals = relationship("ProductSourcing", back_populates="supplier")

# ============================================================
# 2. Product Sourcing (The Real Deal)
# ============================================================
class ProductSourcing(Base):
    __tablename__ = "product_sourcing_std"

    sourcing_id = Column(Integer, primary_key=True, index=True)
    
    # Links
    # Note: Cross-Domain FK to PIM Engine
    product_gtin = Column(String(14), ForeignKey("product_master_std.gtin"), nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("supplier_std.supplier_id"), nullable=False)
    
    # Logistics Logic
    fulfillment_type = Column(Enum(FulfillmentType), default=FulfillmentType.OWNED_INVENTORY, index=True)
    lead_time_days = Column(Integer, default=1, comment="Avg days to ship")
    moq = Column(Integer, default=1, comment="Minimum Order Quantity")
    
    # Codes
    supplier_sku = Column(String(50), nullable=True, comment="Code used in Supplier's system")
    
    # Costing
    cost_price_vat_exclusive = Column(Integer, nullable=False, comment="Supply Price (No VAT)")
    currency = Column(String(3), default="KRW")
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    supplier = relationship("Supplier", back_populates="sourcing_deals")
    batches = relationship("ProductBatch", back_populates="sourcing_source")
    
    # No direct relationship back to ProductMaster defined here to avoid circular imports.
    # PIM side is unaware of SCM details by default.

# ============================================================
# 3. Product Batch (Traceability)
# ============================================================
class ProductBatch(Base):
    __tablename__ = "product_batch_std"
    
    batch_id = Column(Integer, primary_key=True, index=True)
    sourcing_id = Column(Integer, ForeignKey("product_sourcing_std.sourcing_id"), nullable=False)
    
    # Traceability
    lot_number = Column(String(50), nullable=True, comment="Production Lot No")
    harvest_date = Column(Date, nullable=True, comment="For fresh produce")
    expiration_date = Column(Date, nullable=True)
    
    # Inventory
    initial_quantity = Column(Integer, default=0)
    current_quantity = Column(Integer, default=0)
    
    status = Column(Enum(ProductStatus), default=ProductStatus.ACTIVE)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    sourcing_source = relationship("ProductSourcing", back_populates="batches")
