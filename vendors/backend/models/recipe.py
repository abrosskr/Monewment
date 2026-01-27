from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from ..database import Base

class ScrapedRecipe(Base):
    __tablename__ = "scraped_recipes"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    name = Column(String)
    ingredients = Column(JSON)  # Stores list of strings
    image = Column(String, nullable=True)
    
    # Classification results
    classification = Column(JSON, nullable=True)
    classified = Column(Boolean, default=False)
    
    # Processing status
    used = Column(Boolean, default=False)
    
    # Metadata
    collected_at = Column(DateTime(timezone=True), server_default=func.now())

    # Deduplication Fingerprint
    content_hash = Column(String, index=True, nullable=True)
