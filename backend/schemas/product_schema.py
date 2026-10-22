from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from .base_schema import ICTBaseModel

class ProductBase(BaseModel):
    """Cột theo articles.csv của H&M. price là VND (quy đổi ước lượng)."""
    article_id: Optional[str] = None
    product_code: Optional[str] = None
    prod_name: str
    product_type_name: Optional[str] = None
    product_group_name: Optional[str] = None
    colour_group_name: Optional[str] = None
    graphical_appearance_name: Optional[str] = None
    index_group_name: Optional[str] = None
    detail_desc: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    sales_last_week: int = 0
    quantity_in_stock: int = 0
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    """Cập nhật sản phẩm - tất cả field optional"""
    article_id: Optional[str] = None
    product_code: Optional[str] = None
    prod_name: Optional[str] = None
    product_type_name: Optional[str] = None
    product_group_name: Optional[str] = None
    colour_group_name: Optional[str] = None
    graphical_appearance_name: Optional[str] = None
    index_group_name: Optional[str] = None
    detail_desc: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    quantity_in_stock: Optional[int] = None
    is_active: Optional[bool] = None

class ProductQuantityUpdate(BaseModel):
    """Cập nhật số lượng trong kho"""
    quantity_in_stock: int

class ProductResponse(ICTBaseModel, ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
