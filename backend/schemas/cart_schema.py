from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from .base_schema import ICTBaseModel
from .product_schema import ProductResponse

class CartItemAdd(BaseModel):
    product_id: UUID
    quantity: int = 1

class CartItemResponse(ICTBaseModel):
    id: int
    user_id: UUID
    product_id: UUID
    quantity: int
    created_at: datetime
    updated_at: datetime
    product: Optional[ProductResponse] = None