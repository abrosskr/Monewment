from pydantic import BaseModel, Field
from typing import Optional

class HarvestRequest(BaseModel):
    url: str = Field(..., description="Target URL to crawl")
    category: str = Field("recipe", description="Content category (e.g., recipe, ingredient)")
    depth: int = Field(1, ge=1, le=3, description="Crawl depth (1-3)")
