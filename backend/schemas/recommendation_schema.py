from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from .product_schema import ProductResponse

class UserRecommendationResponse(BaseModel):
    product_id: UUID
    score: float
    product_details: Optional[ProductResponse] = None
    rank: int

    class Config:
        from_attributes = True
