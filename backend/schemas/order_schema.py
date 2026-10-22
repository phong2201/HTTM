from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from .base_schema import ICTBaseModel
from .product_schema import ProductResponse

class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: int

class OrderCreate(BaseModel):
    note: Optional[str] = None
    items: List[OrderItemCreate]

class OrderItemResponse(ICTBaseModel):
    id: int
    product_id: UUID
    quantity: int
    unit_price: float
    subtotal: float
    product: Optional[ProductResponse] = None

class OrderResponse(ICTBaseModel):
    id: UUID
    user_id: UUID
    order_date: datetime
    status: int
    total_amount: float
    note: Optional[str] = None
    items: List[OrderItemResponse] = []
    updated_at: datetime