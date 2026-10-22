from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from .base_schema import ICTBaseModel
from .product_schema import ProductResponse

class RecommendationBase(BaseModel):
    product_id: UUID
    recommended_product_id: UUID
    score: float
    rank: int
    version_id: UUID

class UserRecommendationResponse(BaseModel):
    product_id: UUID
    score: float
    product_details: Optional[ProductResponse] = None
    rank: int
    
    class Config:
        from_attributes = True

class PastRecommendationResponse(BaseModel):
    product_id: UUID
    product_details: ProductResponse

    class Config:
        from_attributes = True