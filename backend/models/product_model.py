import uuid
from sqlalchemy import Column, String, Float, TIMESTAMP, func, Boolean, Text, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from database import Base

class Product(Base):
    """Sản phẩm theo articles.csv của dataset H&M (tên/mô tả giữ nguyên tiếng Anh)."""
    __tablename__ = "products"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Định danh H&M: article_id = product_code (7 số) + 3 số biến thể màu
    article_id = Column(String(10), unique=True, nullable=True, index=True)
    product_code = Column(String(7), nullable=True, index=True)

    prod_name = Column(String(255), nullable=False)
    product_type_name = Column(String(100), nullable=True)
    product_group_name = Column(String(100), nullable=True, index=True)
    colour_group_name = Column(String(100), nullable=True)
    graphical_appearance_name = Column(String(100), nullable=True)
    index_group_name = Column(String(100), nullable=True, index=True)
    detail_desc = Column(Text, nullable=True)

    # Giá VND quy đổi ước lượng từ giá chuẩn hóa của H&M (xem settings.HM_PRICE_TO_VND)
    price = Column(Float, nullable=False)
    image_url = Column(String(500), nullable=True)
    sales_last_week = Column(Integer, nullable=False, server_default='0', default=0)
    quantity_in_stock = Column(Integer, nullable=False, server_default='0', default=0)
    is_active = Column(Boolean, default=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    order_items = relationship("OrderItem", back_populates="product", cascade="all, delete-orphan")
    wishlisted_by = relationship("Wishlist", back_populates="product", cascade="all, delete-orphan")
    in_carts = relationship("Cart", back_populates="product", cascade="all, delete-orphan")
    user_interactions = relationship("Interaction", back_populates="product", cascade="all, delete-orphan")
