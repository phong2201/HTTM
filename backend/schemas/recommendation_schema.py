from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from .product_schema import ProductResponse

class UserRecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: UUID
    score: float
    product_details: Optional[ProductResponse] = None
    rank: int
