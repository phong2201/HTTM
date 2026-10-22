import uuid
from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from database import Base

class Cart(Base):
    __tablename__ = "carts"
    __table_args__ = (UniqueConstraint('user_id', 'product_id', name='_user_product_cart_uc'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="in_carts")