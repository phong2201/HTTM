import uuid
from sqlalchemy import Column, Integer, Float, TIMESTAMP, Text, ForeignKey, func, Enum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from database import Base
from enum import Enum as PyEnum

class OrderStatus(int, PyEnum):
    PENDING = 0
    DELIVERING = 1
    COMPLETED = 2
    CANCELLED = 3

class Order(Base):
    __tablename__ = "orders"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    order_date = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    total_amount = Column(Float, nullable=False)
    note = Column(Text, nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(PG_UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey('products.id', ondelete='RESTRICT'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")