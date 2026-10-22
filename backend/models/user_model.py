import uuid
from sqlalchemy import Column, Integer, String, TIMESTAMP, func, Enum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from database import Base
from enum import Enum as PyEnum

class Role(int, PyEnum):
    SELLER = 1
    BUYER = 2
    ADMIN = 3
    DATA_SCIENTIST = 4

class User(Base):
    __tablename__ = "users"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = Column(Enum(Role), nullable=False, default=Role.BUYER)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    gender = Column(String(50), nullable=True)
    age = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships - Dùng string "Order" để tránh import trực tiếp
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    wishlist_items = relationship("Wishlist", back_populates="user", cascade="all, delete-orphan")
    cart_items = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(username={self.username!r}, id={self.id})>"