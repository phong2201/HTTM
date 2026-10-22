from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from .base_schema import ICTBaseModel
from .product_schema import ProductResponse

class WishlistAdd(BaseModel):
    product_id: UUID

class WishlistResponse(ICTBaseModel):
    id: UUID
    user_id: UUID
    product_id: UUID
    created_at: datetime
    product: Optional[ProductResponse] = None