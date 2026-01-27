from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class SourceIngestion(Base):
    """Refinery Step 1: Ingestion (The raw entry point)"""
    __tablename__ = "ingestion_sources"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    raw_data = Column(JSON) # Absolute raw, un-inferred
    collected_at = Column(DateTime(timezone=True), server_default=func.now())

class IngredientAsset(Base):
    """Refinery Step 4: Sealed Asset (Domain: INGREDIENT)"""
    __tablename__ = "asset_domain_ingredient"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("ingestion_sources.id"))
    domain = Column(String, default="INGREDIENT")
    purity_grade = Column(String) # A to D
    
    name = Column(String, index=True)
    scientific_name = Column(String, nullable=True)
    category = Column(String)
    mass_g = Column(Float, nullable=True)
    
    # Strictly NO recipe text or culture info here
    verified_at = Column(DateTime(timezone=True), server_default=func.now())

class CultureAsset(Base):
    """Refinery Step 4: Sealed Asset (Domain: CULTURE)"""
    __tablename__ = "asset_domain_culture"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("ingestion_sources.id"))
    domain = Column(String, default="CULTURE")
    purity_grade = Column(String)
    
    cuisine_type = Column(String, index=True) # e.g. "KOREAN", "KYOTO_STYLE"
    region = Column(String, nullable=True)
    identity_markers = Column(JSON) # list of archetypal ingredient tokens

class MethodAsset(Base):
    """Refinery Step 4: Sealed Asset (Domain: RECIPE_TEXT)"""
    __tablename__ = "asset_domain_method"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("ingestion_sources.id"))
    domain = Column(String, default="RECIPE_TEXT")
    purity_grade = Column(String)
    
    verb = Column(String, index=True) # e.g. "SEAR", "BRAISE"
    sequence_order = Column(Integer)
    duration_min = Column(Float, nullable=True)
    # Strictly NO physical constants here (those belong to PHYSICS domain)

class FoodPhysicsAsset(Base):
    """Refinery Step 4: Sealed Asset (Domain: PHYSICS)"""
    __tablename__ = "asset_domain_physics"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True) # External correlation
    domain = Column(String, default="PHYSICS")
    purity_grade = Column(String, default="A+")
    
    # Physical vectors (Stored as JSON or linked to Parquet)
    thermal_integral = Column(Float)
    moisture_loss_rate = Column(Float)
    maillard_point = Column(Float)
    
    # Strictly NO culture or recipe text here
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

class BehaviorAsset(Base):
    """Refinery Step 4: Sealed Asset (Domain: BEHAVIOR)"""
    __tablename__ = "asset_domain_behavior"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("ingestion_sources.id"))
    domain = Column(String, default="BEHAVIOR")
    purity_grade = Column(String, default="B") # Community Consensus
    
    # Behavioral Primitives (The "Growth" Truth)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    positive_sentiment_ratio = Column(Float, default=0.0)
    subscriber_view_ratio = Column(Float, default=0.0) # SCV
    
    # Taste Score (MS) - Calculated
    ms_score = Column(Float, nullable=True)
    
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

class MenuArchetype(Base):
    """
    [Food Data Factory: Phase 10]
    The "Golden Record" for a specific menu.
    Supports Multi-layering: Core (Fact) and Variant (Context).
    """
    __tablename__ = "menu_archetypes"

    id = Column(Integer, primary_key=True, index=True)
    menu_name = Column(String, unique=True, index=True)
    layer = Column(String) # "CORE", "VARIANT", or "HUMAN_UNSEEN"
    parent_id = Column(Integer, ForeignKey("menu_archetypes.id"), nullable=True) # For Variant/Unseen -> Core linking
    
    culture_context = Column(String, nullable=True) # e.g. "Western", "Quick-Cook", "Molecular"
    initial_state = Column(String, default="ROOM_TEMP") # "FROZEN", "ROOM_TEMP", "PREHEATED"
    semantic_embedding = Column(JSON) # SBERT vector
    
    # Intelligence Metrics
    purity_grade = Column(String, default="A")
    consensus_count = Column(Integer, default=0) # Number of sources supporting this
    physics_optimization_score = Column(Float, nullable=True) # For HUMAN_UNSEEN: Simulation-based improvement
    
    data = Column(JSON) # The actual combined truth (ingredients, methods, steps)
    chemical_metadata = Column(JSON) # Maillard, Oxidation, etc. reactivity data
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
